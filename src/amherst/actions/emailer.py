from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pythoncom
from loguru import logger
from win32com.client import Dispatch

from amherst.config import TEMPLATES


@dataclass
class Email:
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
    Email handler for Outlook (ripped from pawsupport where it has a superclass and siblings for Gmail etc)
    """

    @staticmethod
    def create_open_email(email: Email, html: bool = False):
        """
        Send email via Outlook

        :param email: Email object
        :param html: format email from html input
        :return: None
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


async def subject(*, invoice_num: str | None = None, missing: bool = False, label: bool = False):
    return (
        f'Amherst Radios'
        f'{f"- Invoice {invoice_num} Attached" if invoice_num else ""} '
        f'{"- We Are Missing Kit" if missing else ""} '
        f'{"- Shipping Label Attached" if label else ""}'
    )


async def send_label_email(shipment):
    label = None if shipment.direction == 'out' else shipment.label_file
    body = TEMPLATES.get_template('email_snips/label_email.html').render(label=label, shipment=shipment)
    email = Email(
        to_address=shipment.remote_contact.email_address,
        subject=f'Amherst Radios Shipping{' - Shipping Label Attached' if label else ''}',
        body=body,
        attachment_paths=[label] if label else [],
    )

    OutlookHandler.create_open_email(email, html=True)


async def send_invoice_email(invoice: Path, address: str):
    addrs = set(a.strip() for a in address.split(',') if a.strip())
    addr_str = ', '.join(addrs)
    body = TEMPLATES.get_template('email_snips/invoice_email.html').render(invoice=invoice)
    email = Email(
        to_address=addr_str,
        subject='Amherst Radios Invoice Attached',
        body=body,
        attachment_paths=[invoice.with_suffix('.pdf')],
    )
    OutlookHandler.create_open_email(email, html=True)


# async def build_all_emails(
#     *,
#     shipment: SHIPMENT_TYPES,
#     invoice: Path | None = None,
#     label: Path | None = None,
#     missing: list | None = None,
# ):
#     sections = [TEMPLATES.get_template('email_snips/hi_snip.html').render()]
#     if invoice:
#         sections.append(TEMPLATES.get_template('email_snips/invoice_snip.html').render(invoice=invoice))
#     if missing:
#         sections.append(TEMPLATES.get_template('email_snips/missing_snip.html').render(missing=missing))
#     if label:
#         sections.append(TEMPLATES.get_template('email_snips/label_snip.html').render(label=label, shipment=shipment))
#     sections.append(TEMPLATES.get_template('email_snips/bye_snip.html').render())
#     email_body = '\n'.join(sections)
#     return email_body
