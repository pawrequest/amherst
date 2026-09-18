# /// script
# requires-python = ">=3.13"
# dependencies = [
# "pywin32>=306"
# ]
# ///
import os
import smtplib
from collections.abc import Sequence
from dataclasses import dataclass, field
from email.message import EmailMessage
from pathlib import Path

import pythoncom
import win32com.client


def print_file(filepath: str):
    os.startfile(filepath, 'print')


def invoice_field_to_pdf(invoice_field: str) -> Path:
    invoice_pdf = Path(invoice_field).with_suffix('.pdf')
    if not invoice_pdf.exists():
        raise FileNotFoundError(f'Invoice PDF not found: {invoice_pdf}')
    return invoice_pdf


def print_invoice_pdf(invoice_field: str):
    filepath = invoice_field_to_pdf(invoice_field)
    print_file(str(filepath))


@dataclass
class Email:
    to_address: str
    subject: str
    body: str
    attachment_paths: list[Path] = field(default_factory=list)


def create_open_email_outlook(email: Email, html: bool = False):
    """
    Send email via Outlook

    :param email: Email object
    :param html: format email from html input
    :return: None
    """
    try:
        pythoncom.CoInitialize()

        outlook = win32com.client.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = email.to_address
        mail.Subject = email.subject
        if html:
            mail.HtmlBody = email.body
        else:
            mail.Body = email.body

        for att_path in email.attachment_paths:
            mail.Attachments.Add(str(att_path))
            print(f'DEBUG: Added attachment: {att_path}')
        mail.Display()
    except Exception as e:
        print(f'ERROR: Failed to send email with error: {e}')
        raise ValueError(f'{e.args[0]}')
    finally:
        pythoncom.CoUninitialize()


class SMTPCredentials:
    smtp_server: str
    smtp_port: int
    username: str
    password: str
    use_tls: bool = True


SERVER = 'amherst-smtp.vpop3mail.com'


def send_email_smtp(creds: SMTPCredentials, email: Email, html: bool = False):
    msg = EmailMessage()
    msg['Subject'] = email.subject
    msg['From'] = creds.username
    msg['To'] = email.to_address

    if html:
        msg.add_alternative(email.body, subtype='html')
    else:
        msg.set_content(email.body)

    for att_path in email.attachment_paths:
        with open(att_path, 'rb') as f:
            data = f.read()
            maintype, subtype = 'application', 'octet-stream'
            msg.add_attachment(data, maintype=maintype, subtype=subtype, filename=Path(att_path).name)

    try:
        with smtplib.SMTP(creds.smtp_server, creds.smtp_port) as server:
            if creds.use_tls:
                server.starttls()
            server.login(creds.username, creds.password)
            server.send_message(msg)
    except Exception as e:
        print(f'ERROR: Failed to send email via SMTP: {e}')
        raise


def get_last_email_from_sender(from_address: str):
    outlook = win32com.client.Dispatch('Outlook.Application')
    namespace = outlook.GetNamespace('MAPI')
    inbox = namespace.GetDefaultFolder(6)  # 6 = Inbox

    sender_email = from_address
    filter_str = f"[SenderEmailAddress] = '{sender_email}'"
    filtered_items = inbox.Items.Restrict(filter_str)
    filtered_items.Sort('[ReceivedTime]', True)
    return filtered_items.GetFirst()


async def send_invoice_email(invoice: Path, addresses: Sequence[str]):
    addrs = set(a.strip() for a in addresses if a.strip())
    addr_str = ', '.join(addrs)
    body = 'invoice email body'
    email = Email(
        to_address=addr_str,
        subject='Amherst Radios Invoice Attached',
        body=body,
        attachment_paths=[invoice.with_suffix('.pdf')],
    )
    create_open_email_outlook(email, html=True)


if __name__ == '__main__':
    if res := get_last_email_from_sender('giles@amherst.co.uk'):
        print(res.Subject, res.ReceivedTime, res.SenderEmailAddress)

# messages = inbox.Items
# message = messages.GetLast()  # or filter for the specific message
#
# reply = message.Reply()
# reply.Body = 'Your reply text here\n' + reply.Body
# reply.Display()
