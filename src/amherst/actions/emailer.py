from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pythoncom
from loguru import logger
from win32com.client import Dispatch

from amherst.config import TEMPLATES


@dataclass
class Email:
    """Dataclass representing an email"""

    to_address: str
    subject: str
    body: str
    attachment_paths: list[Path] | None = None

    def __post_init__(self):
        if self.attachment_paths is None:
            self.attachment_paths = []

    def send(self, sender: OutlookHandler) -> None:
        sender.create_open_email(self)


class OutlookHandler:
    """
    Email handler for Outlook
    """

    @staticmethod
    def create_open_email(email: Email, html: bool = False):
        """
        Send email via Outlook

        :param email: Email object
        :return: None

        Args:
            html: Format email as html
        """
        try:
            pythoncom.CoInitialize()

            outlook = Dispatch('outlook.application')
            mail = outlook.CreateItem(0)
            mail.To = email.to_address
            mail.Subject = email.subject
            if html:
                mail.HtmlBody = email.body
            else:
                mail.Body = email.body

            for att_path in email.attachment_paths:
                mail.Attachments.Add(str(att_path))
                print('Added attachment')
            mail.Display()
        except Exception as e:
            logger.exception(f'Failed to send email with error: {e}')
            raise ValueError(f'{e.args[0]}')
        finally:
            pythoncom.CoUninitialize()


async def subject(invoice_num: str | None = None, missing=None, label=None):
    return (
        f'Amherst Radios'
        f'{f"- Invoice {invoice_num} Attached" if invoice_num else ""} '
        f'{"- We Are Missing Kit" if missing else ""} '
        f'{"- Shipping Label Attached" if label else ""}'
    )


async def make_email(addresses: str, invoice: Path, label: Path, missing: str, booking_state):
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


async def make_label_email(addresses: list[str], label: Path):
    email_body = TEMPLATES.get_template('ship/label_email_body.html').render({'label': label, 'dropoff': False})
    addresses = '; '.join(addresses)
    email_obj = Email(
        to_address=addresses,
        subject=label_subject,
        body=email_body,
        attachment_paths=[label],
    )
    return email_obj


async def send_label_email(addresses: list[str], label: Path):
    email: Email = await make_label_email(addresses, label)
    OutlookHandler.create_open_email(email, html=True)


