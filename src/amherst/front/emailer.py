from __future__ import annotations

import typing as _t

import fastapi
from fastui import FastUI, components as c, forms as fastui_forms
from loguru import logger
from pawdantic import paw_strings
from shipaw import Shipment
from suppawt.office_ps import email_handler as eh
from suppawt.office_ps.email_handler import EmailError
from suppawt.office_ps.ms import outlook_handler as oh

from amherst import am_db
from amherst.am_shared import CustomerFields
from amherst.front import support
from amherst.models.am_record import AmherstRecord
from amherst.models.shipment_record import ShipmentRecordInDB
from amherst.front.support import EmailChoices

router = fastapi.APIRouter()


@router.post('/{shiprec_id}', response_model=FastUI, response_model_exclude_none=True)
async def email_post(
        shiprec_id: int,
        recipients: list = fastapi.Form(...),
        invoice: bool = fastapi.Form(False),
        label=fastapi.Form(False),
        missing_kit=fastapi.Form(False),
        session=fastapi.Depends(am_db.get_session),
):
    logger.info(f'email {recipients=}')
    alert_dict = {}
    shiprec = await support.get_shiprec(shiprec_id, session)

    if label:
        if not shiprec.booking_state.label_downloaded:
            alert_dict = {'Label not downloaded': 'Error'}
            return [c.Text(text=str(alert_dict))]
    try:
        email = await generic_email(
            recipients=recipients,
            shiprec=shiprec,
            invoice=invoice,
            missing=missing_kit,
            label=label,
        )
    except ValueError as e:
        alert_dict = {'': str(e)}
        return [c.Text(text=str(alert_dict))]
    try:
        handler = oh.OutlookHandlerMultipleAttachments()
        handler.create_open_email(email)
    except EmailError as e:
        msg = 'Error sending email'
        if '-2147221005' in e.args:
            msg = f'{msg} - Outlook not open'
        alert_dict = {f'{msg} {e}': 'Error'}
        return [c.Text(text=str(alert_dict))]
    return [c.Text(text='Email created and opened')]


class EmailChoiceBoolean(c.FormFieldBoolean):
    """FastUI form field Boolean for email choices."""

    name: EmailChoices




GREETING = 'Hi,\n\nThanks for choosing to hire from Amherst.\n'

INVOICE_BODY = 'Please find your invoice attached.\n'

GOODBYE = 'If you have any queries please let us know.\n\nKind Regards,\nAmherst Enterprises'


def label_body(state: Shipment):
    return f"""Please find a pre-paid parcelforce label attached – it needs to be printed and attached to the box.
Please ensure any old postage labels are removed or thoroughly obscured as otherwise the parcel may be delivered back to you instead of coming home!'
{collection_str(state) if state.direction == 'in' else ''}
"""


def collection_str(shipment: Shipment):
    return f"""Collection is booked for {paw_strings.date_string(shipment.ship_date)}, 
we are unable to give precise timings, however you should receive notifications at the contact details below:'
{support.shipment_notification_labels_str(shipment)}

If for any reason the courier is missed you can drop the labelled box at any uk postoffice.
"""


def missing_kit_body(missing: _t.Sequence[str]):
    missing_items = '\n'.join(missing)
    return f"""Thanks for returning the hired equipment - I hope it worked well for your event.
    
Unfortunately the return was missing the following items - can you please look/check with
colleagues to see if they can be recovered - otherwise I'll draw up an invoice for replacement."
MISSING KIT:

{missing_items}

(If you have already discussed missing items with us please disregard this automatically generated email)
"""


def compose_body(
        state: Shipment = None,
        item: AmherstRecord = None,
        invoice: bool = False,
        missing_kit: bool = False,
        label: bool = False,
):
    missing_strs = item.MISSING_KIT.splitlines() if missing_kit else []
    return f"""{GREETING}
{INVOICE_BODY if invoice else ""}
{missing_kit_body(missing_strs) if missing_kit else ""}
{label_body(state) if label else ""}
{GOODBYE}
"""


async def generic_email(
        recipients: list[str],
        shiprec: ShipmentRecordInDB = None,
        label: bool = False,
        missing: bool = False,
        invoice: bool = False,
) -> eh.Email:
    """Get an Email object for sending an invoice, missing kit request, or shipping-label.

    Args:
        recipients: List of email addresses.
        shiprec: The shiprec object.
        label: Whether to include the shipping label.
        missing: Whether to include the missing kit request.
        invoice: Whether to include the invoice.

    Returns:
        Email: The email object.
    """
    if shiprec.record.cmc_table_name == 'Customer':
        if invoice:
            raise ValueError("Customers don't have invoices")
        if missing:
            raise ValueError("Customers don't have missing kit")

    invoice_pdf_path = None
    invoice_num = None
    label_path = None

    addresses = '; '.join(recipients)
    if invoice:
        invoice_pdf_path = shiprec.record.invoice.with_suffix('.pdf')
        invoice_num = invoice_pdf_path.stem

    if label:
        try:
            label_path = shiprec.booking_state.label_dl_path
        except AttributeError:
            raise ValueError('Label not downloaded')

    return eh.Email(
        to_address=addresses,
        subject=await subject(invoice_num, missing, label),
        body=compose_body(shiprec.shipment, shiprec.record, invoice, missing, label),
        attachment_paths=[x for x in [invoice_pdf_path, label_path] if x],
    )


def get_email_options(shiprec: ShipmentRecordInDB):
    # irec = shiprec.record
    # crec = shiprec.item.customer_record

    rec_type = shiprec.record.cmc_table_name

    state_delivery = shiprec.shipment.contact.email_address
    record_delivery = shiprec.record.email

    customer_accounts = shiprec.record.customer_record.get(CustomerFields.ACCOUNTS_EMAIL)
    customer_primary = shiprec.record.customer_record.get(CustomerFields.PRIMARY_EMAIL)
    customer_default_del = shiprec.record.customer_record.get(CustomerFields.DELIVERY_EMAIL)
    customer_invoice = shiprec.record.customer_record.get(CustomerFields.INVOICE_EMAIL)

    addr_dict = {
        state_delivery: f'from shipper ({state_delivery})',
        customer_accounts: f'customer accounts ({customer_accounts})',
        customer_primary: f'customer primary ({customer_primary})',
        customer_default_del: f'customer default delivery ({customer_default_del})',
        customer_invoice: f'customer invoice ({customer_invoice})',
        record_delivery: f'{rec_type} delivery ({record_delivery})',
    }

    return [fastui_forms.SelectOption(value=k, label=v) for k, v in addr_dict.items() if k]


# async def send_label(shiprec: managers.MANAGER_IN_DB):
#     """Send the label by email."""
#     email = await generic_email(
#         recipients=[shiprec.shipment.contact.email_address],
#         shiprec=shiprec,
#         label=True,
#     )
#     handler = oh.OutlookHandlerMultipleAttachments()
#     handler.create_open_email(email)


# def send_label1(shipment: shipaw.ShipState):
#     """Send the label by email."""
#     email = email_templates.return_label_email(shipment)
#     handler = oh.OutlookHandler()
#     handler.send_email(email)


# async def send_missing(shiprec: managers.MANAGER_IN_DB):
#     email = await generic_email(
#         recipients=[shiprec.shipment.contact.email_address],
#         shipment=shiprec.shipment,
#         item=shiprec.item,
#     )
#     handler = oh.OutlookHandlerMultipleAttachments()
#     handler.create_open_email(email)


# async def send_invoice(shiprec: managers.BookingManagerOut):
#     """Send invoice by email."""
#     # email = await email_templates.invoice_email(shiprec)
#     email = await generic_email(
#         recipients=[shiprec.shipment.contact.email_address],
#         invoice=await support.get_invoice_path(shiprec.item)
#     )
#     handler = oh.OutlookHandlerMultipleAttachments()
#     handler.create_open_email(email)


async def subject(invoice_num: str = None, missing: bool = None, label: bool = False):
    return (
        f'Radio Hire - '
        f'{f"Invoice {invoice_num} Attached" if invoice_num else ""} '
        f'{"Missing Kit" if missing else ""} '
        f'{"Shipping Label Attached" if label else ""}'
    ).strip()
