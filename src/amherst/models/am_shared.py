from __future__ import annotations

from enum import Enum, StrEnum
from typing import Literal

from pycommence.api import CmcFilter, Connection, FilterArray

SALE_CUSTOMERS = Connection(
    name='SaleCustomers',
    to_table='Customers',
    from_table='Sale',
)

HIRE_CUSTOMERS = Connection(
    name='HireCustomers',
    to_table='Customers',
    from_table='Hire',
)

HireStatusType = Literal[
    'Booked in',
    'Booked in and packed',
    'Partially packed',
    'Out',
    'Returned all OK',
    'Returned with problems',
    'Quote given',
    'Cancelled',
    'Extended',
    'Sold To Customer',
    '',
]


class HireStatusEnum(StrEnum):
    BOOKED_IN = 'Booked in'
    PACKED = 'Booked in and packed'
    PARTIALLY_PACKED = 'Partially packed'
    OUT = 'Out'
    RTN_OK = 'Returned all OK'
    RTN_PROBLEMS = 'Returned with problems'
    QUOTE_GIVEN = 'Quote given'
    CANCELLED = 'Cancelled'
    EXTENDED = 'Extended'
    SOLD = 'Sold To Customer'


INITIAL_FILTER_ARRAY = FilterArray(
    filters={
        1: CmcFilter(
            cmc_col='Status',
            condition='Equal To',
            value='Booked in',
        ),
        2: CmcFilter(
            cmc_col='Send Out Date',
            condition='After',
            value='2023-01-01',
        ),
    }
)

INITIAL_FILTER_ARRAY2 = FilterArray().add_filters(
    CmcFilter(cmc_col='Status', condition='Equal To', value='Booked in'),
    CmcFilter(
        cmc_col='Send Out Date',
        condition='After',
        value='2023-01-01',
    ),
)


class HireFields(str, Enum):
    ACTUAL_RETURN_DATE = 'Actual Return Date'
    DELIVERY_ADDRESS = 'Delivery Address'
    AERIAL_ADAPT = 'Number Aerial Adapt'
    ALL_ADDRESS = 'All Address'
    BATTERIES = 'Number Batteries'
    BOOKED_DATE = 'Booked Date'
    BOXES = 'Boxes'
    BUSINESS_NAME = 'Delivery Name'
    CASES = 'Number Cases'
    CLIPON_AERIAL = 'Number Clipon Aerial'
    CLOSED = 'Closed'
    DELIVERY_CONTACT = 'Delivery Contact'
    CUSTOMER = 'To Customer'
    DB_LABEL_PRINTED = 'DB label printed'
    DELIVERY_COST = 'Delivery Cost'
    DISCOUNT_DESCRIPTION = 'Discount Description'
    DISCOUNT_PERCENTAGE = 'Discount Percentage'
    DUE_BACK_DATE = 'Due Back Date'
    EM = 'Number EM'
    DELIVERY_EMAIL = 'Delivery Email'
    EMC = 'Number EMC'
    HEADSET = 'Number Headset'
    HEADSET_BIG = 'Number Headset Big'
    ICOM = 'Number Icom'
    ICOM_CAR_LEAD = 'Number ICOM Car Lead'
    ICOM_PSU = 'Number ICOM PSU'
    INVOICE = 'Invoice'
    MAGMOUNT = 'Number Magmount'
    MEGAPHONE = 'Number Megaphone'
    MEGAPHONE_BAT = 'Number Megaphone Bat'
    MISSING_KIT = 'Missing Kit'
    NAME = 'Name'
    PACKED_BY = 'Packed By'
    PACKED_DATE = 'Packed Date'
    PACKED_TIME = 'Packed Time'
    PARROT = 'Number Parrot'
    PAYMENT_TERMS = 'Payment Terms'
    PICKUP_ARRANGED = 'Pickup Arranged'
    DELIVERY_POSTCODE = 'Delivery Postcode'
    PURCHASE_ORDER = 'Purchase Order'
    RADIO_TYPE = 'Radio Type'
    RECURRING_HIRE = 'Recurring Hire'
    REFERENCE_NUMBER = 'Reference Number'
    REPEATER = 'Number Repeater'
    REPROGRAMMED = 'Reprogrammed'
    RETURN_NOTES = 'Return Notes'
    SENDING_STATUS = 'Sending Status'
    SEND_COLLECT = 'Send / Collect'
    SEND_METHOD = 'Send Method'
    SEND_OUT_DATE = 'Send Out Date'
    SGL_CHARGER = 'Number Sgl Charger'
    SPECIAL_KIT = 'Special Kit'
    STATUS = 'Status'
    DELIVERY_TELEPHONE = 'Delivery Tel'
    SALE_TELEPHONE = 'Delivery Telephone'
    TRACKING_NUMBERS = 'Tracking Numbers'
    UHF = 'Number UHF'
    UHF_6WAY = 'Number UHF 6-way'
    UNPACKED_BY = 'Unpacked by'
    UNPACKED_DATE = 'Unpacked Date'
    UNPACKED_TIME = 'Unpacked Time'
    VHF = 'Number VHF'
    VHF_6WAY = 'Number VHF 6-way'
    WAND = 'Number Wand'
    WAND_BAT = 'Number Wand Battery'
    WAND_CHARGER = 'Number Wand Charger'


class CustomerFields(str, Enum):
    SEND_OUT_DATE = 'dummy'
    BOXES = 'dummy'

    NAME = 'Name'
    DELIVERY_ADDRESS = 'Deliv Address'
    DELIVERY_CONTACT = 'Deliv Contact'
    DELIVERY_EMAIL = 'Deliv Email'
    DELIVERY_NAME = 'Deliv Name'
    DELIVERY_POSTCODE = 'Deliv Postcode'
    DELIVERY_TELEPHONE = 'Deliv Telephone'


class SaleFields(str, Enum):
    BOXES = 'dummy'
    SEND_OUT_DATE = 'dummy'

    CUSTOMER = 'To Customer'
    NAME = 'Name'
    LOST_EQUIPMENT = 'Lost Equipment'
    STATUS = 'Status'
    DATE_ORDERED = 'Date Ordered'
    DATE_SENT = 'Date Sent'
    INVOICE_TERMS = 'Invoice Terms'
    INVOICE = 'Invoice'
    PURCHASE_ORDER_PRINT = 'Purchase Order Print'
    PURCHASE_ORDER = 'Purchase Order'
    ITEMS_ORDERED = 'Items Ordered'
    SERIAL_NUMBERS = 'Serial Numbers'
    ORDER_PACKED_BY = 'Order Packed By'
    ORDER_TAKEN_BY = 'Order Taken By'
    DELIVERY_METHOD = 'Delivery Method'
    OUTBOUND_ID = 'Outbound ID'
    NOTES = 'Notes'
    DELIVERY_NOTES = 'Delivery Notes'
    DELIVERY_ADDRESS = 'Delivery Address'
    DELIVERY_CONTACT = 'Delivery Contact'
    DELIVERY_EMAIL = 'Delivery Email'
    DELIVERY_NAME = 'Delivery Name'
    DELIVERY_POSTCODE = 'Delivery Postcode'
    DELIVERY_TELEPHONE = 'Delivery Telephone'
    INVOICE_ADDRESS = 'Invoice Address'
    INVOICE_CONTACT = 'Invoice Contact'
    INVOICE_EMAIL = 'Invoice Email'
    INVOICE_NAME = 'Invoice Name'
    INVOICE_POSTCODE = 'Invoice Postcode'
    INVOICE_TELEPHONE = 'Invoice Telephone'


def addr_lines_dict_am(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    return {f'address_line{num}': line for num, line in enumerate(addr_lines, start=1)}
