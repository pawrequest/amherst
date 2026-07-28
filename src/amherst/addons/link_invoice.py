# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "pycommence==0.2.4",
# ]
# ///
import argparse
import sys

from pycommence import pycommence_context


def link_cmc_invoice(category, record_name, invoice_path, invoice_field: str = 'Invoice'):
    with pycommence_context(category) as pycmc:
        updater = {invoice_field: str(invoice_path)}
        pycmc.update_row(updater, pk=record_name)
        print('Success')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Link an invoice file to a Commence record.')
    parser.add_argument('category', help='Commence category name (e.g. Hire)')
    parser.add_argument('record_name', help='Name of the record to update')
    parser.add_argument('invoice_path', help='Path to the invoice file')
    parser.add_argument('--field', default='Invoice', help='Field name to update (default: Invoice)')
    args = parser.parse_args()
    link_cmc_invoice(args.category, args.record_name, args.invoice_path, args.field)
    sys.exit(0)
