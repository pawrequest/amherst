"""
Wrap FastAPI app in FlaskWebGUI for desktop application.
Use `Paw Request fork <https://github.com/pawrequest/flaskwebgui>`_ for URL_SUFFIX to dynamically set loading page to the retrieved record

Environment variables:
    AM_ENV: Path to environment file defining:
        - log file location
    SHIP_ENV: Path to environment file defining:
        - parcelforce account numbers
        - parcelforce contract numbers
        - parcelforce username and password
        - parcelforce wsdl
        - parcelforce endpoint
        - parcelforce binding
        - parcelforce live status

"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

import pyperclip

from amherst.actions import print_file
from amherst.actions.emailer import send_invoice_email
from amherst.actions.invoice_number import next_inv_num
from amherst.actions.payment_status import get_payment_status, invoice_num_from_path
from amherst.models.commence_adaptors import CategoryName


def shipper_cli():
    from amherst.set_env import set_amherstpr_env
    from amherst.ui_runner import shipper
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=CategoryName, choices=list(CategoryName))
    arg_parser.add_argument('record_name', type=str)
    arg_parser.add_argument('--sandbox', action='store_true', help='Run in sandbox mode')
    args1 = arg_parser.parse_args()
    set_amherstpr_env(sandbox=args1.sandbox)
    if 'trial' in args1.category.name.lower():
        args1.category = CategoryName.Trial
    args1.category = CategoryName(args1.category.title())
    args = args1
    asyncio.run(shipper(args.category, args.record_name))


def file_printer_cli():
    parser = argparse.ArgumentParser(description='Print a file using the default printer.')
    parser.add_argument('file_path', type=str, help='Path to the file to print')
    args = parser.parse_args()
    file_path = args.file_path
    if not os.path.exists(file_path):
        print(f'File not found: {file_path}')
        sys.exit(1)
    print_file(file_path)


def send_invoice_email_cli():
    parser = argparse.ArgumentParser(description='Send an invoice email with attachment.')
    parser.add_argument('invoice', type=Path, help='Path to the invoice PDF')
    parser.add_argument('address', type=str, help='Recipient email address')
    args = parser.parse_args()
    asyncio.run(send_invoice_email(args.invoice, args.address))


def payment_status_cli():
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
