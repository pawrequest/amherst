"""
Wrap FastAPI app in FlaskWebGUI for desktop application.
Use `Paw Request fork <https://github.com/pawrequest/flaskwebgui>`_ for URL_SUFFIX to dynamically set loading page to the retrieved record
"""

import argparse
import asyncio
import os
import sys
import webbrowser
from pathlib import Path

import dotenv
import pyperclip
from loguru import logger

from amherst.actions import print_file
from amherst.actions.convert_tracking import convert_parcelforce_tracking_to_royal_mail
from amherst.actions.invoice_number import next_inv_num
from amherst.actions.payment_status import get_payment_status, invoice_num_from_path
from amherst.models.commence_adaptors import CategoryName
from amherst.office_am.merge_docs.box_label import commence_box_label


def shipper_cli():
    args = parse_ship_args()
    logger.info(f'starting shipper for {args.category} {args.record_name} with env {args.env_index}')
    os.environ['ENV_INDEX'] = str(args.env_index)
    dotenv.load_dotenv(args.env_index)
    from amherst.ui_runner import pycommence_shipper  # AFTER SETTING ENVIRONMENT

    asyncio.run(pycommence_shipper(args.category, args.record_name))


def parse_ship_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=CategoryName, choices=list(CategoryName))
    arg_parser.add_argument('record_name', type=str)
    arg_parser.add_argument('env_index', type=Path)
    args = arg_parser.parse_args()
    return args


def file_printer_cli():
    parser = argparse.ArgumentParser(description='Print a file using the default printer.')
    parser.add_argument('file_path', type=str, help='Path to the file to print')
    args = parser.parse_args()
    file_path = args.file_path
    if not os.path.exists(file_path):
        print(f'File not found: {file_path}')
        sys.exit(1)
    print_file(file_path)


#
# def send_invoice_email_cli():
#     from amherst.actions.emailer import send_invoice_email
#     parser = argparse.ArgumentParser(description='Send an invoice email with attachment.')
#     parser.add_argument('invoice', type=Path, help='Path to the invoice PDF')
#     parser.add_argument('address', type=str, help='Recipient email address')
#     args = parser.parse_args()
#     asyncio.run(send_invoice_email(args.invoice, args.address))


def payment_status_cli():
    parser = argparse.ArgumentParser(description='Check invoice payment status')
    parser.add_argument('invoice_number', type=str, help='Invoice number to check')
    parser.add_argument('accounts_spreadsheet', type=Path, help='Path to accounts spreadsheet', nargs='?')
    args = parser.parse_args()
    inv_num = invoice_num_from_path(args.invoice_number)
    print(f"\n Payment Status for {inv_num} is '{get_payment_status(inv_num, args.accounts_spreadsheet)}'\n")


def payment_status_cli1():
    parser = argparse.ArgumentParser(description='Check invoice payment status')
    parser.add_argument('invoice_number', type=str, help='Invoice number to check')
    parser.add_argument('accounts_spreadsheet', type=Path, help='Path to accounts spreadsheet', nargs='?')
    args = parser.parse_args()
    inv_num = invoice_num_from_path(args.invoice_number)
    accs_file = args.accounts_spreadsheet or Path(r'R:\ACCOUNTS\ye2025\ac2425.xls')
    print(get_payment_status(inv_num, accs_file))


def next_invoice_cli():
    res = next_inv_num()
    pyperclip.copy(res)
    print(f'next available invoice number is {res} and is copied to clipboard')
    sys.exit(0)


def convert_tracking_link():
    parser = argparse.ArgumentParser(description='Convert old Parcelforce tracking URL to Royal Mail tracking URL.')
    parser.add_argument('old_track_url', type=str, help='The old Parcelforce tracking URL to convert.')
    args = parser.parse_args()
    url = convert_parcelforce_tracking_to_royal_mail(args.old_track_url)
    webbrowser.open(url, new=2)


def generate_box_label_cli():
    parser = argparse.ArgumentParser(description='Generate box labels for a record.')
    parser.add_argument('category', type=CategoryName, choices=list(CategoryName), help='Category of the record.')
    parser.add_argument('record_name', type=str, help='Name of the record.')
    parser.add_argument('amherst_env', type=Path, help='Path to the Amherst environment file.')
    args = parser.parse_args()
    logger.info(f'Generating box labels for {args.category} {args.record_name} with env {args.amherst_env}')
    commence_box_label(category=args.category, pk=args.record_name, amherst_env=args.amherst_env)
