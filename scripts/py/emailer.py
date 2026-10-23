# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "jinja2>=3.1.6",
#     "pywin32>=306",
#     "starlette>=1.9.0",
# ]
# ///
# import asyncio
import argparse
import os
import smtplib
import sys
from argparse import Namespace
from dataclasses import dataclass, field
from email.message import EmailMessage
from pathlib import Path

import pythoncom
import win32com.client
from starlette.templating import Jinja2Templates

THIS_PATH = Path(__file__)
TEMPLATE_DIR = THIS_PATH.parent.parent / 'templates'


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


# async def create_open_invoice_email(invoice: Path, addresses: Sequence[str]):
#     addrs = {a.strip() for a in addresses if a.strip()}
#     addr_str = '; '.join(addrs)
#     body = await _render_invoice_email(invoice)
#
#     email = Email(
#         to_address=addr_str,
#         subject='Amherst Radios Invoice Attached',
#         body=body,
#         attachment_paths=[invoice.with_suffix('.pdf')],
#     )
#     create_open_email_outlook(email, html=True)


# async def _render_invoice_email(invoice: Path) -> Any:
#     templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
#     body = templates.get_template('email_snips/invoice_email.html').render(invoice=invoice)
#     return body


def main():
    parser = argparse.ArgumentParser(description='Create and open an email in Outlook.')
    parser.add_argument('--address', required=True, help='Recipient address (comma/semicolon separated for multiple)')
    parser.add_argument('--subject', default='', help='Email subject')
    parser.add_argument('--body', default='', help='Email body')
    parser.add_argument('--template', help='Jinja Template')
    parser.add_argument('--html', action='store_true', help='Treat body as HTML')
    parser.add_argument('--debug', action='store_true', help='pause to read prints')
    parser.add_argument(
        '--attachment',
        action='append',
        default=[],
        dest='attachments',
        help='Path to an attachment (repeatable, e.g. --attachment a.pdf --attachment b.pdf)',
    )
    args = parser.parse_args()

    if args.template and args.template == 'invoice_email.html':
        apply_invoice_template(args)

    email = Email(
        to_address=args.address,
        subject=args.subject,
        body=args.body,
        attachment_paths=args.attachments,
    )
    create_open_email_outlook(email, html=args.html)
    if args.debug:
        res = input('paused')
    return 0


def apply_invoice_template(args: Namespace):
    print('invoice template')
    try:
        args.attachments = convert_word_attachment_args(args.attachments)
        args.subject = f'Amherst Radio Hire: Invoice {args.attachments[0].stem}'
        templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
        invoice_template = templates.get_template(args.template)
        args.body = invoice_template.render(invoice=args.attachments[0])
        args.html = True
    except Exception as e:
        print(e)
        sys.exit(1)


def convert_word_attachment_args(attachments: list[Path]) -> list[Path]:
    print('convert atatchments')
    attached = []
    for a in attachments:
        a = Path(a)
        print('try convert :', a)
        if a.suffix.lower() in ['.doc', '.docx']:
            print('Converting attachment suffix from MSWord to PDF')
            a = a.with_suffix('.pdf')
        attached.append(a)
    print(attached)
    return attached


if __name__ == '__main__':
    sys.exit(main())
