from enum import Enum
from pathlib import Path

from suppawt.office_ps.email_handler import Email

DEBUG = True
USE_MICROSOFT = False


class DFLT_PATHS:
    ROOT = Path(__file__).parent
    STATIC = ROOT / 'static'
    DATA = STATIC / 'data'
    GENERATED = STATIC / 'generated'
    TEMPLATE = STATIC / 'templates'
    AST_WB = DATA / 'assets.xlsx'
    PRC_WB = DATA / 'prices.xlsx'
    AST_OUT = GENERATED / 'assets_out.xlsx'
    PRC_OUT = GENERATED / 'prices_out.xlsx'
    PRCS_JSON = PRC_OUT.with_suffix('.json')
    INV_TMPLT = TEMPLATE / 'invoice_tmplt.docx'
    INV_DIR_MOCK = GENERATED / 'mock_invoices'
    INV_OUT_DIR = INV_DIR_MOCK
    INV_DIR = Path(r'R:\ACCOUNTS\invoices')
    TEMP_INV = INV_OUT_DIR / '_temp_invoice.docx'
    TEMP_DOC = GENERATED / '_temp_doc.docx'
    BOX_TMPLT = TEMPLATE / 'box_tmplt_rebuild.docx'


class DFLT_CONST:
    FW_VERSION = 'XXXX'
    MIN_DUR = 'Min Duration'
    MODEL = 'Model'
    SERIAL = 'Barcode'
    ID = 'Number'
    FW = 'FW'
    MIN_QTY = 'Min Qty'
    PRICE = 'Price'
    AST_SHEET = 'Sheet1'
    AST_HEAD: int = 2
    PRC_HEAD: int = 0


DFLT_HIRE_EMAIL: Email = Email(
    to_address='pythonsnake48@gmail.com',
    subject='Radio Hire - Invoice attached',
    body='Please find attached the invoice for your hire.',
)


def get_hire_invoice_email(hire: dict) -> Email:
    to_address = hire['Email']
    subject = 'Radio Hire - Invoice attached'
    nl = '\n'
    body = f'Thanks for hiring from amherst, your order contains the following: {nl*2}{hire["Hire Sheet Text"]}'
    return Email(to_address, subject, body)



class DTYPES:
    HIRE_PRICES = {
        'Name': 'string',
        'Description': 'string',
        'Min Qty': 'int',
        'Min Duration': 'int',
        'Price': 'float',
    }
    HIRE_RECORD = {
        'Items': 'string',
        'Closed': 'bool',
        'Reference Number': 'string',
        'Weeks': 'int',
        'Boxes': 'int',
        'Recurring': 'bool',
        'Delivery Cost': 'float',
    }
    SALE_PRICES = {key: value for key, value in HIRE_PRICES.items() if key != 'Min Duration'}


class FIELDS:
    CUSTOMER = [
        'Contact Name',
        'Name',
        'Address',
        'Postcode',
        'Charity?',
        'Discount Percentage',
        'Email',
    ]
    HIRE = [
        'Delivery Contact',
        'Delivery Name',
        'Delivery Address',
        'Delivery Postcode',
        'Number UHF',
        'Booked Date',
        'Name',
    ]
    SALE = [
        'Invoice Address',
        'Name',
    ]
    FREE_ITEMS = [
        'Sgl Charger',
        'UHF 6-way',
        'Wand Battery',
        'ICOM PSU',
        'Megaphone Bat',
        'ICOM Car Lead',
        'Magmount',
        'Clipon Aerial',
        'Wand Charger',
        'Aerial Adapt',
    ]


NOT_HIRE = ['Min Duration', 'Closed']


def format_currency(value):
    # return value
    # return f' £ {value:.2f}'
    if value == '':
        return ''
    # if isinstance(value, str):
    #     value = Decimal(value)
    return f"£{value:>8.2f}"
