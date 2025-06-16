from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pythoncom
from fastapi import Form
from loguru import logger
from shipaw.models.pf_shipment import Shipment
from shipaw.ship_types import ShipDirection
from win32com.client import Dispatch

from amherst.config import TEMPLATES
from amherst.models.amherst_models import AMHERST_SHIPMENT_TYPES


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


async def make_email(
    *,
    shipment: AMHERST_SHIPMENT_TYPES,
    addresses: str,
    invoice: Path | None = None,
    label: Path | None = None,
    missing: list | None = None,
):
    email_body = TEMPLATES.get_template('email_body.html').render(
        {
            'shipment': shipment,
            'invoice': invoice,
            'label': label,
            'missing': missing,
        }
    )
    subject_str = await subject(
        invoice_num=invoice.stem if invoice else None, missing=missing is not False, label=label is not False
    )
    email_obj = Email(
        to_address=addresses,
        subject=subject_str,
        body=email_body,
        attachment_paths=[x for x in [label, invoice] if x],
    )
    return email_obj


label_subject = f'Amherst Radios - Shipping Label Attached'


async def make_label_email(*, shipment: Shipment):
    label = shipment.label_file
    addresses = shipment.recipient_contact.email_address
    em = await make_email(shipment=shipment, addresses=addresses, label=label)
    return em


async def send_label_email(shipment: Shipment):
    email: Email = await make_label_email(shipment=shipment)
    OutlookHandler.create_open_email(email, html=True)

