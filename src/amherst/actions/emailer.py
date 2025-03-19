from __future__ import annotations

from suppawt.office_ps.email_handler import Email
from suppawt.office_ps.ms.outlook_handler import OutlookHandler

from amherst.config import TEMPLATES


async def subject(invoice_num: str | None = None, missing=None, label=None):
    return (
        f'Amherst Radios'
        f'{f"- Invoice {invoice_num} Attached" if invoice_num else ""} '
        f'{"- We Are Missing Kit" if missing else ""} '
        f'{"- Shipping Label Attached" if label else ""}'
    )


async def make_email(addresses, invoice, label, missing, booking_state):
    email_body = TEMPLATES.get_template('email_body.html').render(
        {
            'booking_state': booking_state,
            'invoice': invoice,
            'label': label,
            'missing': missing,
        }
    )
    subject_str = await subject(invoice.stem if invoice else None, missing is not False, label is not False)
    email_obj = Email(
        to_address=addresses,
        subject=subject_str,
        body=email_body,
        attachment_paths=[x for x in [label, invoice] if x],
    )
    return email_obj


label_subject = f'Amherst Radios - Shipping Label Attached'


async def make_label_email(addresses, label):
    email_body = TEMPLATES.get_template('label_email_body.html').render({'label': label})
    email_obj = Email(
        to_address=addresses,
        subject=label_subject,
        body=email_body,
        attachment_paths=[label],
    )
    return email_obj


async def send_label_email(addresses, label):
    email: Email = await make_label_email(addresses, label)
    OutlookHandler().create_open_email(email)


