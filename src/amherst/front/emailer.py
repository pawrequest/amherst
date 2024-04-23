from __future__ import annotations

import typing as _t

import fastapi
from fastui import FastUI, components as c, forms as fastui_forms
from loguru import logger
from pawdantic import paw_strings
from suppawt.office_ps import email_handler as eh
from suppawt.office_ps.email_handler import EmailError
from suppawt.office_ps.ms import outlook_handler as oh

from amherst import am_db, am_types
from amherst.front import support
from amherst.models import managers
from amherst.models.am_record import AmherstRecord
from shipaw.ship_ui import states

router = fastapi.APIRouter()


@router.post('/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def email_post(
    manager_id: int,
    recipients: list = fastapi.Form(...),
    invoice: bool = fastapi.Form(False),
    label=fastapi.Form(False),
    missing_kit=fastapi.Form(False),
    session=fastapi.Depends(am_db.get_session),
):
    logger.info(f'email {recipients=}')
    alert_dict = {}
    manager = await support.get_manager(manager_id, session)

    if label:
        if not manager.state.booking_state.label_downloaded:
            alert_dict = {'Label not downloaded': 'Error'}
            return [c.Text(text=str(alert_dict))]
    try:
        email = await generic_email(
            recipients=recipients,
            manager=manager,
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

    name: am_types.EmailChoices


def get_email_form(manager: managers.MANAGER_IN_DB, choices: list[am_types.EmailChoices]):
    bool_fields = [EmailChoiceBoolean(name=k, title=k.title()) for k in choices]

    return c.Form(
        form_fields=[
            c.FormFieldSelect(
                name='recipients',
                title='recipients',
                multiple=True,
                options=get_email_options(manager),
            ),
            *bool_fields,
        ],
        submit_url=f'/api/email/{manager.id}',
    )


GREETING = 'Hi,\n\nThanks for choosing to hire from Amherst.\n'

INVOICE_BODY = 'Please find your invoice attached.\n'

GOODBYE = 'If you have any queries please let us know.\n\nKind Regards,\nAmherst Enterprises'


def label_body(state: states.ShipState):
    return f"""Please find a pre-paid parcelforce label attached – it needs to be printed and attached to the box.
Please ensure any old postage labels are removed or thoroughly obscured as otherwise the parcel may be delivered back to you instead of coming home!'
Collection is booked for {paw_strings.date_string(state.ship_date)}, we are unable to give precise timings, however you should receive notifications at the contact details below:'

{support.state_notification_labels_str(state)}

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
    state: states.ShipState = None,
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
    manager: managers.MANAGER_IN_DB = None,
    label: bool = False,
    missing: bool = False,
    invoice: bool = False,
) -> eh.EmailMultipleAttachments:
    """Get an Email object for sending an invoice, missing kit request, or shipping-label.

    Args:
        recipients: List of email addresses.
        manager: The manager object.
        label: Whether to include the shipping label.
        missing: Whether to include the missing kit request.
        invoice: Whether to include the invoice.

    Returns:
        EmailMultipleAttachments: The email object.
    """
    if manager.record.cmc_table_name == 'Customer':
        if invoice:
            raise ValueError("Customers don't have invoices")
        if missing:
            raise ValueError("Customers don't have missing kit")

    invoice_pdf_path = None
    invoice_num = None
    label_path = None

    addresses = '; '.join(recipients)
    if invoice:
        invoice_pdf_path = manager.record.invoice.with_suffix('.pdf')
        invoice_num = invoice_pdf_path.stem

    if label:
        try:
            label_path = manager.state.booking_state.label_dl_path
        except AttributeError:
            raise ValueError('Label not downloaded')

    return eh.EmailMultipleAttachments(
        to_address=addresses,
        subject=await subject(invoice_num, missing, label),
        body=compose_body(manager.state, manager.record, invoice, missing, label),
        attachment_paths=[x for x in [invoice_pdf_path, label_path] if x],
    )


def get_email_options(manager: managers.MANAGER_IN_DB):
    # irec = manager.record
    # crec = manager.item.customer_record

    state_delivery = manager.state.contact.email_address

    addr_dict = {
        state_delivery: f'from current state ({state_delivery})',
    }

    return [fastui_forms.SelectOption(value=k, label=v) for k, v in addr_dict.items() if k]


# async def send_label(manager: managers.MANAGER_IN_DB):
#     """Send the label by email."""
#     email = await generic_email(
#         recipients=[manager.state.contact.email_address],
#         manager=manager,
#         label=True,
#     )
#     handler = oh.OutlookHandlerMultipleAttachments()
#     handler.create_open_email(email)


# def send_label1(state: shipaw.ShipState):
#     """Send the label by email."""
#     email = email_templates.return_label_email(state)
#     handler = oh.OutlookHandler()
#     handler.send_email(email)


# async def send_missing(manager: managers.MANAGER_IN_DB):
#     email = await generic_email(
#         recipients=[manager.state.contact.email_address],
#         state=manager.state,
#         item=manager.item,
#     )
#     handler = oh.OutlookHandlerMultipleAttachments()
#     handler.create_open_email(email)


# async def send_invoice(manager: managers.BookingManagerOut):
#     """Send invoice by email."""
#     # email = await email_templates.invoice_email(manager)
#     email = await generic_email(
#         recipients=[manager.state.contact.email_address],
#         invoice=await support.get_invoice_path(manager.item)
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
