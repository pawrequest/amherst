from __future__ import annotations

import functools
from datetime import date, timedelta
from enum import Enum, StrEnum
from typing import Annotated

import pydantic as _p
from loguru import logger
from pydantic import Field

from pycommence.pycmc_types import (
    Connection,
    get_cmc_date,
    to_cmc_date,
)
from pycommence.filters import ConditionType, ConnectedFieldFilter, FieldFilter, FilterArray, SortOrder
from shipaw.ship_types import limit_daterange_no_weekends

LOCATION = 'HM'


class AmherstTableName(StrEnum):
    Hire = 'Hire'
    Sale = 'Sale'
    Customer = 'Customer'


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


@functools.lru_cache
def initial_filter(filtername: str) -> FilterArray:
    hire_start = date.today() - timedelta(days=30)
    hire_end = date.today() + timedelta(days=30)
    sale_start = '1 month ago'
    if LOCATION == 'HM':
        hire_start = date.today() - timedelta(days=400)
        hire_end = date.today() + timedelta(days=30)
        sale_start = '18 months ago'

    sorts = None
    match filtername:
        case 'Hire':
            fils = hires_in_range_fils(hire_start, hire_end)
            sorts = ((HireAliases.SEND_DATE, SortOrder.ASC),)
            res = FilterArray.from_filters(*fils, sorts=sorts)

        case 'Sale':
            fils = (FieldFilter(column=SaleAliases.DATE_ORDERED, condition=ConditionType.AFTER, value=sale_start),)
            res = FilterArray.from_filters(*fils, sorts=sorts)

        case 'Customer':
            # fils = (
            #     FieldFilter(
            #         column=CustomerAliases.DATE_LAST_CONTACTED, condition=ConditionType.AFTER, value=lastcontact
            #     ),
            # )
            fils = (
                ConnectedFieldFilter.model_validate(
                    dict(
                        column='Has Hired',
                        connection_category='Hire',
                        connected_column=HireAliases.SEND_DATE,
                        condition=ConditionType.AFTER,
                        value='12 months ago'
                    )
                ),
                ConnectedFieldFilter.model_validate(
                    dict(
                        column='Involves',
                        connection_category='Sale',
                        connected_column=SaleAliases.DATE_ORDERED,
                        condition=ConditionType.AFTER,
                        value='12 months ago'
                    )
                ),
            )
            res = FilterArray.from_filters(
                *fils,
                sorts=sorts,
                logic='Or, And, And'
                # logic='And, And, And'
            )

        case _:
            raise ValueError(f'No filter for {filtername}')

    return res


class CustomerAliases(str, Enum):
    NAME = 'Name'
    CUSTOMER_NAME = 'Name'

    DELIVERY_ADDRESS_STR = 'Deliv Address'
    DELIVERY_CONTACT_NAME = 'Deliv Contact'
    DELIVERY_CONTACT_EMAIL = 'Deliv Email'
    DELIVERY_CONTACT_BUSINESS = 'Deliv Name'
    DELIVERY_ADDRESS_PC = 'Deliv Postcode'
    DELIVERY_CONTACT_PHONE = 'Deliv Telephone'

    INVOICE_EMAIL = 'Invoice Email'
    ACCOUNTS_EMAIL = 'Accounts Email'

    INVOICE_ADDRESS = 'Invoice Address'
    INVOICE_CONTACT = 'Invoice Contact'
    INVOICE_NAME = 'Invoice Name'
    INVOICE_POSTCODE = 'Invoice Postcode'
    INVOICE_TELEPHONE = 'Invoice Telephone'
    PRIMARY_EMAIL = 'Email'
    DATE_LAST_CONTACTED = 'Date Last Contact'


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
    SEND_DATE = 'Send Out Date'
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


def hires_in_range_fils(start_date: date, end_date: date | None = None) -> tuple[FieldFilter, ...]:
    fils = (
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.CANCELLED),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
        FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.AFTER, value=to_cmc_date(start_date)),
    )
    if end_date:
        fils += (
            FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.BEFORE, value=to_cmc_date(end_date)),
        )
    return fils


def get_alias(tablename: str, field_name: str) -> str:
    match tablename:
        case 'Hire':
            return HireAliases[field_name].value()


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
    field_name = field_name.upper()
    if hasattr(SaleAliases, field_name):
        return getattr(SaleAliases, field_name).value
    return field_name


AM_DATE = Annotated[
    date,
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
