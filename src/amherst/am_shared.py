from __future__ import annotations

from enum import Enum, StrEnum

from pycommence import FilterArray, pycmc_types
from pycommence.pycmc_types import CmcFilter

SALE_CUSTOMERS = pycmc_types.Connection(
    name='SaleCustomers',
    to_table='Customers',
    from_table='Sale',
)

HIRE_CUSTOMERS = pycmc_types.Connection(
    name='HireCustomers',
    to_table='Customers',
    from_table='Hire',
)


class HireStatus(StrEnum):
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


class HireFields(str, Enum):
    ARRANGED_OUTBOUND = 'DB label printed'
    ARRANGED_INBOUND = 'Pickup Arranged'
    ACTUAL_RETURN_DATE = 'Actual Return Date'
    AERIAL_ADAPT = 'Number Aerial Adapt'
    ALL_ADDRESS = 'All Address'
    BATTERIES = 'Number Batteries'
    BOOKED_DATE = 'Booked Date'
    BOXES = 'Boxes'
    BUSINESS_NAME = 'Delivery Name'
    CASES = 'Number Cases'
    CLIPON_AERIAL = 'Number Clipon Aerial'
    CLOSED = 'Closed'
    CUSTOMER = 'To Customer'
    DB_LABEL_PRINTED = 'DB label printed'
    DELIVERY_ADDRESS = 'Delivery Address'
    DELIVERY_CONTACT = 'Delivery Contact'
    DELIVERY_COST = 'Delivery Cost'
    DELIVERY_EMAIL = 'Delivery Email'
    DELIVERY_POSTCODE = 'Delivery Postcode'
    DELIVERY_TELEPHONE = 'Delivery Tel'
    DISCOUNT_DESCRIPTION = 'Discount Description'
    DISCOUNT_PERCENTAGE = 'Discount Percentage'
    DUE_BACK_DATE = 'Due Back Date'
    EM = 'Number EM'
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
    PICKUP_DATE = 'Pickup Date'
    PURCHASE_ORDER = 'Purchase Order'
    RADIO_TYPE = 'Radio Type'
    RECURRING_HIRE = 'Recurring Hire'
    REFERENCE_NUMBER = 'Reference Number'
    REPEATER = 'Number Repeater'
    REPROGRAMMED = 'Reprogrammed'
    RETURN_NOTES = 'Return Notes'
    SALE_TELEPHONE = 'Delivery Telephone'
    SENDING_STATUS = 'Sending Status'
    SEND_COLLECT = 'Send / Collect'
    SEND_METHOD = 'Send Method'
    SEND_OUT_DATE = 'Send Out Date'
    SGL_CHARGER = 'Number Sgl Charger'
    SPECIAL_KIT = 'Special Kit'
    STATUS = 'Status'
    TRACK_INBOUND = 'Track Inbound'
    TRACK_OUTBOUND = 'Track Outbound'
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
    INVOICE_ADDRESS = 'Invoice Address'
    INVOICE_CONTACT = 'Invoice Contact'
    INVOICE_EMAIL = 'Invoice Email'
    INVOICE_NAME = 'Invoice Name'
    INVOICE_POSTCODE = 'Invoice Postcode'
    INVOICE_TELEPHONE = 'Invoice Telephone'
    ACCOUNTS_EMAIL = 'Accounts Email'
    PRIMARY_EMAIL = 'Email'
    CUSTOMER = 'Name'


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


INITIAL_FILTER_ARRAY = FilterArray(
    filters={
        1: CmcFilter(cmc_col=HireFields.STATUS, value=f'{HireStatus.PACKED}'),
        2: CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition='After', value='one week ago'),
        3: CmcFilter(cmc_col=HireFields.SEND_OUT_DATE, condition='Before', value='one week from now'),
    }
)
