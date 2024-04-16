from __future__ import annotations

import pathlib
import typing as _t

import fastapi
from fastui import FastUI, components as c, forms as fastui_forms

import shipr
from amherst import am_db
from amherst.front import email_templates, support
from amherst.models import am_shared, managers
from shipr.ship_ui import states
from suppawt.office_ps import email_handler as eh
from suppawt.office_ps.ms import outlook_handler as oh

router = fastapi.APIRouter()

greeting = 'Hi,\n\nThanks for choosing to hire from Amherst.'

invoice_body = 'Please find your invoice attached.'

goodbye = 'If you have any queries please let us know.\nKind Regards,\nAmherst Enterprises'


def label_body(state: states.ShipState):
    return (
        'Please find a pre-paid parcelforce label attached – it needs to be printed and attached to the box.'
        'Please ensure any old postage labels are removed or thoroughly obscured as otherwise the parcel may be delivered back to you instead of coming home!'
        'Collection is booked for {paw_strings.date_string(state.ship_date)}, we are unable to give precise timings, however you should receive notifications at the contact details below:'
        f'{support.state_notification_labels_str(state)}'
        'If for any reason the courier is missed you can drop the labelled box at any uk postoffice.'
        'Any issues please let us know'
        'Kind Regards\nAmherst Enterprises'
    )


def missing_kit_body(missing: _t.Sequence[str]):
    missing_items = '\n'.join(missing)
    return (
            "Thanks for returning the hired equipment - I hope it worked well for your event.\n\n"
            "Unfortunately the return was missing the following items - can you please look/check with "
            "colleagues to see if they can be recovered - otherwise I'll draw up an invoice for replacement.\n"
            "MISSING KIT:\n" +
            missing_items +
            '\n\n(If you have already discussed missing items with us please disregard this automatically generated email)'
    )


def compose_body(
        invoice: pathlib.Path = None,
        label_path: pathlib.Path | None = None,
        missing: _t.Sequence[str] = None
):
    body_parts = [greeting]
    if invoice:
        body_parts.append(invoice_body)
    if missing:
        body_parts.append(missing_kit_body(missing))
    if label_path:
        body_parts.append('Please find your shipping label attached.')
    body_parts.append(goodbye)
    return '\n\n'.join(body_parts)


async def generic_email(
        recipients: _t.Sequence[str],
        invoice: pathlib.Path = None,
        missing: _t.Sequence[str] = None,
        label_path: pathlib.Path = None,
) -> eh.EmailMultipleAttachments:
    if not any([invoice, missing, label_path]):
        raise ValueError('No email type specified')
    addresses = '; '.join(recipients)
    return eh.EmailMultipleAttachments(
        to_address=addresses,
        subject=await subject(invoice, missing, label_path),
        body=compose_body(invoice, missing),
        attachment_paths=[x for x in [invoice, label_path] if x],
    )


async def subject(
        invoice: pathlib.Path = None,
        missing: _t.Sequence = None,
        label: pathlib.Path = None
):
    invoice_num = await support.get_invoice_num(invoice) if invoice else None

    return (f'Radio Hire - '
            f'{f"Invoice {invoice_num} Attached" if invoice else ""} '
            f'{"Missing Kit" if missing else ""} '
            f'{"Shipping Label Attached" if label else ""}'
            ).strip()


async def send_generic(
        recipients: _t.Sequence[str],
        manager: managers.MANAGER_IN_DB,
        invoice: bool = False,
        missing: bool = False,
        label: bool = False
):
    if not any([invoice, missing, label]):
        raise ValueError('No email type specified')
    invoice_path = await support.get_invoice_path(manager) if invoice else None
    missing = await support.get_missing(manager) if missing else None
    label_path = None
    if label:
        if not manager.state.booking_state.label_downloaded:
            raise ValueError('label not downloaded')
        label_path = manager.state.booking_state.label_dl_path

    email = await generic_email(
        recipients=recipients,
        invoice=invoice_path,
        missing=missing,
        label_path=label_path,
    )
    handler = oh.OutlookHandlerMultipleAttachments()
    handler.send_email(email)


def send_label(state: shipr.ShipState):
    """Send the label by email."""
    email = email_templates.return_label_email(state)
    handler = oh.OutlookHandler()
    handler.send_email(email)


async def send_missing(manager: managers.MANAGER_IN_DB):
    missing = await support.get_missing(manager)
    email = await generic_email(
        recipients=[manager.state.contact.email_address],
        missing=missing
    )
    handler = oh.OutlookHandlerMultipleAttachments()
    handler.send_email(email)


async def send_invoice(manager: managers.BookingManagerOut):
    """Send invoice by email."""
    # email = await email_templates.invoice_email(manager)
    email = await generic_email(
        recipients=[manager.state.contact.email_address],
        invoice=await support.get_invoice_path(manager)
    )
    handler = oh.OutlookHandlerMultipleAttachments()
    handler.send_email(email)


def get_email_options(manager: managers.MANAGER_IN_DB):
    addr_dict = {
        manager.state.contact.email_address: 'delivery',
        manager.item.customer_record.get(am_shared.CustomerFields.INVOICE_EMAIL): 'invoice',
        manager.item.customer_record.get(am_shared.CustomerFields.ACCOUNTS_EMAIL): 'accounts',
    }
    return [fastui_forms.SelectOption(value=k, label=v)
            for k, v in addr_dict.items() if k
            ]


def get_email_form(manager: managers.MANAGER_IN_DB):
    return c.Form(
        submit_url=f'/api/forms/email/{manager.id}',
        form_fields=[
            c.FormFieldBoolean(
                name='invoice',
                title='invoice',
            ),
            c.FormFieldBoolean(
                name='label',
                title='label',
            ),
            c.FormFieldBoolean(
                name='missing_kit',
                title='missing kit',
            ),

            c.FormFieldSelect(
                name='recipients',
                title='recipients',
                multiple=True,
                options=get_email_options(manager),
            ),
        ],
    )


async def generic_email_div(manager: managers.MANAGER_IN_DB):
    return c.Div(
        class_name='row my-3',
        components=[
            get_email_form(manager)
        ]
    )
