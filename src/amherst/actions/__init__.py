# from .file_printer import file_printer_cli
# from .emailer import send_invoice_email
# from .invoice_number import next_invoice_cli
#
# __all__ = [
#     'send_invoice_email',
#     'file_printer_cli',
#     'next_invoice_cli',
# ]
import os


def print_file(filepath):
    try:
        os.startfile(filepath, 'print')
        print(f'Printing {filepath}')
    except Exception as e:
        print(f'Error: {e}')
