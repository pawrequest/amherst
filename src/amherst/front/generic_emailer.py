from __future__ import annotations

import pathlib
import typing as _t

import shipr
from amherst.front import support, email_templates
from amherst.models import managers
from suppawt.office_ps import email_handler
from suppawt.office_ps.ms.outlook_handler import OutlookHandler

greeting = 'Hi,\n\nThanks for choosing to hire from Amherst.'

invoice_body = 'Please find your invoice attached.'

goodbye = 'If you have any queries please let us know.\nKind Regards,\nAmherst Enterprises'


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


def write_body(invoice: pathlib.Path = None, missing: _t.Sequence[str] = None):
    body_parts = [greeting]
    if invoice:
        body_parts.append(invoice_body)
    if missing:
        body_parts.append(missing_kit_body(missing))
    body_parts.append(goodbye)
    return '\n\n'.join(body_parts)


async def generic_email(
        recipient: str,
        invoice: pathlib.Path = None,
        missing: _t.Sequence[str] = None,
        label_path: pathlib.Path = None,
) -> email_handler.Email:
    if not any([invoice, missing, label_path]):
        raise ValueError('No email type specified')
    return email_handler.Email(
        to_address=recipient,
        subject=await subject(invoice, missing is not None, label_path is not None),
        body=write_body(invoice, missing),
        attachment_path=invoice if invoice else None,
    )


async def subject(invoice: pathlib.Path, missing: bool, label: bool):
    invoice_num = await support.get_invoice_num(invoice) if invoice else None

    return f'Radio Hire - {f"Invoice {invoice_num} Attached" if invoice else ""} {"Missing Kit" if missing else ""} {"Shipping Label Attached" if label else ""}'.strip()

#
# def write_body(invoice: pathlib.Path = None, missing: _t.Sequence[str] = None):
#     return f"""{greeting}
#     {invoice_body if invoice else ''}
#     {missing_kit_body(missing) if missing else ''}
#     {goodbye}
#     """
#
#
# def get_email(
#         recipient: str,
#         invoice: pathlib.Path = None,
#         missing: _t.Sequence[str] = None
# ) -> email_handler.Email:
#     if not any([invoice, missing]):
#         raise ValueError('No email type specified')
#     return email_handler.Email(
#         to_address=recipient,
#         subject=f'Radio Hire - {"Invoice Attached" if invoice else ''} {"Missing Kit" if missing else ''}',
#         body=write_body(invoice, missing),
#         attachment_path=invoice if invoice else None,
#     )


# greeting = """Hi,
#
#     Thanks for choosing to hire from Amherst.
# """
#
# invoice_body = """ Please find attached the invoice for your recent hire from Amherst. """
#
# goodbye = """If you have any queries please let us know.
#     Kind Regards
#     Amherst Enterprises
# """


#
# def missing_kit_body(missing: _t.Sequence[str]):
#     return f"""Thanks for returning the hired equipment - I hope it worked well for your event.
#
#     Unfortunately the return was missing the following items - can you please look/check with colleagues to see if they can be recovered - otherwise i'll draw up an invoice for replacement.
#     Kind regards,
#     the Amherst team
#
#     MISSING KIT:
#     {'\n'.join([_ for _ in missing])}
#
#     (If you have already discussed missing items with us please disregard this automatically generated email)
# """
async def send_generic(manager: managers.MANAGER_IN_DB, invoice:bool = False, missing:bool = False, label:bool=False):
    if not any([invoice, missing, label]):
        raise ValueError('No email type specified')
    if invoice:
        invoice_path = await support.get_invoice_path(manager)
    if missing:
        missing = await support.get_missing(manager)
    if label:
        if not manager.state.booking_state.label_downloaded:
            raise ValueError('label not downloaded')
        label_path = manager.state.booking_state.label_dl_path
    email = await generic_emailer.generic_email()


def send_label(state: shipr.ShipState):
    """Send the label by email."""
    email = email_templates.return_label_email(state)
    handler = OutlookHandler()
    handler.send_email(email)


async def send_missing(manager: managers.MANAGER_IN_DB):
    missing = await support.get_missing(manager)
    email = await generic_emailer.generic_email(
        recipient=manager.state.contact.email_address,
        missing=missing
    )
    handler = OutlookHandler()
    handler.send_email(email)


async def send_invoice(manager: managers.BookingManagerOut):
    """Send invoice by email."""
    # email = await email_templates.invoice_email(manager)
    email = await generic_emailer.generic_email(
        recipient=manager.state.contact.email_address,
        invoice=await support.get_invoice_path(manager)
    )
    handler = OutlookHandler()
    handler.send_email(email)
