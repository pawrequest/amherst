from __future__ import annotations

import re
from abc import ABC
from datetime import date
from enum import Enum, StrEnum
from typing import Annotated

import pydantic as _p
from pydantic import Field

from pycommence.pycmc_types import (
    Connection,
    get_cmc_date,
)
from shipaw.ship_types import limit_daterange_no_weekends

LOCATION = 'HM'


class AmherstTableName(StrEnum):
    Hire = 'Hire'
    Sale = 'Sale'
    Customer = 'Customer'
    Trial = 'Radio Trial'


# SALE_CUSTOMERS = Connection(
#     name='SaleCustomers',
#     to_table='Customers',
#     from_table='Sale',
# )
#
# HIRE_CUSTOMERS = Connection(
#     name='HireCustomers',
#     to_table='Customers',
#     from_table='Hire',
# )


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
    SOLD = 'Sold to customer'


class AbstractAmherstShipable(str, ABC):
    NAME: str
    CUSTOMER_NAME: str

    DELIVERY_CONTACT_BUSINESS: str
    DELIVERY_CONTACT_NAME: str
    DELIVERY_CONTACT_EMAIL: str
    DELIVERY_CONTACT_PHONE: str

    DELIVERY_ADDRESS_STR: str
    DELIVERY_ADDRESS_PC: str


class AmherstCustomerShipable(AbstractAmherstShipable):
    Name: str = 'Name'


class CustomerAliases(str, Enum):
    NAME = 'Name'
    CUSTOMER_NAME = 'Name'

    DELIVERY_CONTACT_NAME = 'Deliv Contact'
    DELIVERY_CONTACT_EMAIL = 'Deliv Email'
    DELIVERY_CONTACT_BUSINESS = 'Deliv Name'
    DELIVERY_CONTACT_PHONE = 'Deliv Telephone'

    DELIVERY_ADDRESS_STR = 'Deliv Address'
    DELIVERY_ADDRESS_PC = 'Deliv Postcode'

    INVOICE_EMAIL = 'Invoice Email'
    ACCOUNTS_EMAIL = 'Accounts Email'

    INVOICE_ADDRESS = 'Invoice Address'
    INVOICE_CONTACT = 'Invoice Contact'
    INVOICE_NAME = 'Invoice Name'
    INVOICE_POSTCODE = 'Invoice Postcode'
    INVOICE_TELEPHONE = 'Invoice Telephone'
    PRIMARY_EMAIL = 'Email'
    DATE_LAST_CONTACTED = 'Date Last Contact'

    HIRES = 'Has Hired Hire'
    SALES = 'Involves Sale'


class HireAliases(StrEnum):
    NAME = 'Name'
    CUSTOMER_NAME = 'To Customer'

    DELIVERY_CONTACT_BUSINESS = 'Delivery Name'
    DELIVERY_CONTACT_NAME = 'Delivery Contact'
    DELIVERY_CONTACT_EMAIL = 'Delivery Email'
    DELIVERY_CONTACT_PHONE = 'Delivery Tel'

    DELIVERY_ADDRESS_STR = 'Delivery Address'
    DELIVERY_ADDRESS_PC = 'Delivery Postcode'

    BOXES = 'Boxes'
    SEND_DATE = 'Send Out Date'
    DELIVERY_METHOD = 'Send Method'
    INVOICE = 'Invoice'
    ARRANGED_OUT = 'DB label printed'
    ARRANGED_IN = 'Pickup Arranged'
    TRACK_OUT = 'Track Outbound'
    TRACK_IN = 'Track Inbound'
    MISSING_KIT_STR = 'Missing Kit'

    ACTUAL_RETURN_DATE = 'Actual Return Date'
    AERIAL_ADAPT = 'Number Aerial Adapt'
    ALL_ADDRESS = 'All Address'
    BATTERIES = 'Number Batteries'
    BOOKED_DATE = 'Booked Date'
    CASES = 'Number Cases'
    CLIPON_AERIAL = 'Number Clipon Aerial'
    CLOSED = 'Closed'
    DB_LABEL_PRINTED = 'DB label printed'
    DELIVERY_COST = 'Delivery Cost'
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
    MAGMOUNT = 'Number Magmount'
    MEGAPHONE = 'Number Megaphone'
    MEGAPHONE_BAT = 'Number Megaphone Bat'
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
    SGL_CHARGER = 'Number Sgl Charger'
    SPECIAL_KIT = 'Special Kit'
    STATUS = 'Status'
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


class SaleAliases(StrEnum):
    CUSTOMER_NAME = 'To Customer'
    NAME = 'Name'

    DELIVERY_CONTACT_BUSINESS = 'Delivery Name'
    DELIVERY_CONTACT_NAME = 'Delivery Contact'
    DELIVERY_CONTACT_EMAIL = 'Delivery Email'
    DELIVERY_CONTACT_PHONE = 'Delivery Telephone'

    DELIVERY_ADDRESS_STR = 'Delivery Address'
    DELIVERY_ADDRESS_PC = 'Delivery Postcode'

    BOXES = 'Boxes'
    SEND_DATE = 'Date Ordered'
    DELIVERY_METHOD = 'Delivery Method'
    INVOICE = 'Invoice'
    ARRANGED_OUT = 'DB label printed'
    ARRANGED_IN = 'Pickup Arranged'
    TRACK_OUT = 'Track Outbound'
    TRACK_IN = 'Track Inbound'
    MISSING_KIT_STR = 'Missing Kit'

    LOST_EQUIPMENT = 'Lost Equipment'
    STATUS = 'Status'
    DATE_ORDERED = 'Date Ordered'
    DATE_SENT = 'Date Sent'
    INVOICE_TERMS = 'Invoice Terms'
    PURCHASE_ORDER_PRINT = 'Purchase Order Print'
    PURCHASE_ORDER = 'Purchase Order'
    ITEMS_ORDERED = 'Items Ordered'
    SERIAL_NUMBERS = 'Serial Numbers'
    ORDER_PACKED_BY = 'Order Packed By'
    ORDER_TAKEN_BY = 'Order Taken By'
    OUTBOUND_ID = 'Outbound ID'
    NOTES = 'Notes'
    DELIVERY_NOTES = 'Delivery Notes'
    INVOICE_ADDRESS = 'Invoice Address'
    INVOICE_CONTACT = 'Invoice Contact'
    INVOICE_EMAIL = 'Invoice Email'
    INVOICE_NAME = 'Invoice Name'
    INVOICE_POSTCODE = 'Invoice Postcode'
    INVOICE_TELEPHONE = 'Invoice Telephone'


class TrialAliases(StrEnum):
    NAME = 'Name'
    CUSTOMER_NAME = 'Involves Customer'

    DELIVERY_CONTACT_BUSINESS = 'Trial Name'
    DELIVERY_CONTACT_NAME = 'Trial Contact'
    DELIVERY_CONTACT_EMAIL = 'Trial Email'
    DELIVERY_CONTACT_PHONE = 'Trial Telephone'

    DELIVERY_ADDRESS_STR = 'Trial Address'
    DELIVERY_ADDRESS_PC = 'Trial Postcode'

    INVOICE = 'Our Invoice'
    # ARRANGED_OUT = 'DB label printed'
    ARRANGED_IN = 'Pickup Arranged'
    TRACK_OUT = 'Track Outbound'
    TRACK_IN = 'Track Inbound'


# def get_alias(tablename: str, field_name: str) -> str:
#     match tablename:
#         case 'Hire':
#             return HireAliases[field_name].value()


def hire_alias(field_name: str) -> str:
    field_name = field_name.upper()
    if hasattr(HireAliases, field_name):
        return getattr(HireAliases, field_name).value
    return field_name


def customer_alias(field_name: str) -> str:
    field_name = field_name.upper()
    if hasattr(CustomerAliases, field_name):
        return getattr(CustomerAliases, field_name).value
    return field_name


def sale_alias(field_name: str) -> str:
    # return get_alias('Sale', field_name)
    field_name = field_name.upper()
    if hasattr(SaleAliases, field_name):
        return getattr(SaleAliases, field_name).value
    return field_name


def trial_alias(field_name: str) -> str:
    field_name = field_name.upper()
    if hasattr(TrialAliases, field_name):
        return getattr(TrialAliases, field_name).value
    return field_name


AM_DATE = Annotated[
    date | None,
    _p.BeforeValidator(get_cmc_date),
]
AM_SHIP_DATE = Annotated[
    date,
    Field(date.today(), alias='Send Out Date'),
    _p.BeforeValidator(limit_daterange_no_weekends),
    _p.BeforeValidator(get_cmc_date),
]


def addr_lines_dict_am(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    return {f'address_line{num}': line for num, line in enumerate(addr_lines, start=1)}


class EmailOption(_p.BaseModel):
    email: str
    description: str
    name: str

    def __eq__(self, other: EmailOption):
        return self.email == other.email


"""
hires in range
sales in range
customers in hires
customers in sales
customers in range
"""


def get_ref(record_name: str):
    # EXCEPT REFS ARE NEITHER UNIQUE NOR GENUINELY PERSISTENT LOL
    match = re.search(r'(ref \d+)', record_name)
    if match:
        return match.group()
    if '/' not in record_name:
        # todo better check to exclude non customer records which should hav refs
        return record_name
    raise ValueError(f'No ref found in {record_name} and has slashes i.e. maybe date')
