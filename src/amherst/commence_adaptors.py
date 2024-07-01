from __future__ import annotations

import functools
from datetime import date
from enum import Enum, StrEnum
from typing import Annotated

import pydantic as _p

from pycommence.pycmc_types import CmcFilter, ConditionType, Connection, FilterArray, get_cmc_date, to_cmc_date

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


class CustomerAliases(str, Enum):
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
    DATE_LAST_CONTACTED = 'Date Last Contact'


class HireAliases(StrEnum):
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


class SaleAliases(StrEnum):
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


class HireAliases2(StrEnum):
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
    DELIVERY_COST = 'Delivery Cost'
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


class SaleAliases2(StrEnum):
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


@functools.lru_cache
def initial_filter(tablename: str) -> FilterArray:
    match tablename:
        case 'Hire':
            fils = hires_in_range_fils(
                date(2023, 5, 1), date(2023, 7, 31)
            )

        case 'Sale':
            fils = (CmcFilter(cmc_col=SaleAliases.DATE_ORDERED, condition=ConditionType.AFTER, value='2 years ago'),)
        case 'Customer':
            fils = (
                CmcFilter(
                    cmc_col=CustomerAliases.DATE_LAST_CONTACTED,
                    condition=ConditionType.AFTER,
                    value='2 years ago'
                ),
            )

        case _:
            raise ValueError(f'No initial filter for {tablename}')

    return FilterArray.from_filters(*fils)


def hires_in_range_fils(start_date: date, end_date: date):
    return (
        CmcFilter(cmc_col=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.CANCELLED),
        CmcFilter(cmc_col=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
        CmcFilter(cmc_col=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
        CmcFilter(cmc_col=HireAliases.SEND_OUT_DATE, condition=ConditionType.AFTER, value=to_cmc_date(start_date)),
        CmcFilter(cmc_col=HireAliases.SEND_OUT_DATE, condition=ConditionType.BEFORE, value=to_cmc_date(end_date)),
    )


def get_alias(tablename: str, field_name: str) -> str:
    match tablename:
        case 'Hire':
            return HireAliases2[field_name].value()


COMMON_FIELDS_MAP = {
    'name': 'Name',
    'category': 'category',
}

DELIV_FIELDS_MAP = {
    'delivery_contact_name': 'Deliv Contact',
    'delivery_contact_email': 'Deliv Email',
    'delivery_contact_business': 'Deliv Name',
    'delivery_contact_phone': 'Deliv Telephone',

    'delivery_address_str': 'Deliv Address',
    'delivery_address_pc': 'Deliv Postcode'
}

DELIVERY_FIELDS_MAP = {
    'delivery_contact_name': 'Delivery Contact',
    'delivery_contact_email': 'Delivery Email',
    'delivery_contact_business': 'Delivery Name',
    'delivery_contact_phone': 'Delivery Telephone',
    'delivery_address_str': 'Delivery Address',
    'delivery_address_pc': 'Delivery Postcode'
}

INVOICE_FIELDS_MAP = {
    'invoice_contact': 'Invoice Contact',
    'invoice_email': 'Invoice Email',
    'invoice_business': 'Invoice Name',
    'invoice_telephone': 'Invoice Telephone',
    'invoice_address_str': 'Invoice Address',
    'invoice_postcode': 'Invoice Postcode'
}

CUSTOMER_FIELDS_MAP = COMMON_FIELDS_MAP | INVOICE_FIELDS_MAP | DELIV_FIELDS_MAP
CUSTOMER_FIELDS_MAP.update(
    {
        'customer_name': 'Name',
        'accounts_email': 'Accounts Email',
        'primary_email': 'Email',

        'date_last_contact': 'Date Last Contact'
    }
)

ORDER_FIELDS_MAP = COMMON_FIELDS_MAP | DELIVERY_FIELDS_MAP
ORDER_FIELDS_MAP.update(
    {
        'customer_name': 'To Customer',
        'arranged_out': 'DB label printed',
        'arranged_in': 'Pickup Arranged',
        'track_out': 'Track Outbound',
        'track_in': 'Track Inbound',
        'status': 'Status',
        'invoice': 'Invoice',
        'purchase_order': 'Purchase Order'
    }
)

HIRE_FIELDS_MAP = ORDER_FIELDS_MAP.copy()
HIRE_FIELDS_MAP.update(
    {
        # overrides
        'date_ordered': 'Booked Date',
        'delivery_method': 'Send Method',
        'delivery_contact_phone': 'Delivery Tel',
        'payment_terms': 'Payment Terms',
        'missing_kit_str': 'Missing Kit',
        'send_date': 'Send Out Date',
        'arranged_in': 'Pickup Arranged',
        'boxes': 'Boxes',

        # unused unique to hire
        'actual_return_date': 'Actual Return Date',
        'aerial_adapt': 'Number Aerial Adapt',
        'batteries': 'Number Batteries',
        'cases': 'Number Cases',
        'clipon_aerial': 'Number Clipon Aerial',
        'closed': 'Closed',
        'delivery_cost': 'Delivery Cost',
        'discount_description': 'Discount Description',
        'discount_percentage': 'Discount Percentage',
        'due_back_date': 'Due Back Date',
        'em': 'Number EM',
        'emc': 'Number EMC',
        'headset': 'Number Headset',
        'headset_big': 'Number Headset Big',
        'icom': 'Number Icom',
        'icom_car_lead': 'Number ICOM Car Lead',
        'icom_psu': 'Number ICOM PSU',
        'magmount': 'Number Magmount',
        'megaphone': 'Number Megaphone',
        'megaphone_bat': 'Number Megaphone Bat',
        'packed_by': 'Packed By',
        'packed_date': 'Packed Date',
        'packed_time': 'Packed Time',
        'parrot': 'Number Parrot',
        'pickup_date': 'Pickup Date',
        'radio_type': 'Radio Type',
        'recurring_hire': 'Recurring Hire',
        'reference_number': 'Reference Number',
        'repeater': 'Number Repeater',
        'reprogrammed': 'Reprogrammed',
        'return_notes': 'Return Notes',
        'sending_status': 'Sending Status',
        'send_collect': 'Send / Collect',
        'sgl_charger': 'Number Sgl Charger',
        'special_kit': 'Special Kit',
        'uhf': 'Number UHF',
        'uhf_6way': 'Number UHF 6-way',
        'unpacked_by': 'Unpacked by',
        'unpacked_date': 'Unpacked Date',
        'unpacked_time': 'Unpacked Time',
        'vhf': 'Number VHF',
        'vhf_6way': 'Number VHF 6-way',
        'wand': 'Number Wand',
        'wand_bat': 'Number Wand Battery',
        'wand_charger': 'Number Wand Charger',
    }
)

SALE_FIELDS_MAP = (ORDER_FIELDS_MAP | INVOICE_FIELDS_MAP).copy()
SALE_FIELDS_MAP.update(
    {
        'delivery_method': 'Delivery Method',
        'lost_equipment': 'Lost Equipment',
        'date_ordered': 'Date Ordered',
        'payment_terms': 'Invoice Terms',
        'items_ordered': 'Items Ordered',
        'serial_numbers': 'Serial Numbers',
        'order_packed_by': 'Order Packed By',
        'order_taken_by': 'Order Taken By',
        'delivery_notes': 'Delivery Notes'
    }
)


def get_hire_alias(field_name: str) -> str:
    return HIRE_FIELDS_MAP.get(field_name, '')


def get_customer_alias(field_name: str) -> str:
    return CUSTOMER_FIELDS_MAP.get(field_name, '')


def get_sale_alias(field_name: str) -> str:
    return SALE_FIELDS_MAP.get(field_name, '')


AM_DATE = Annotated[
    date,
    _p.BeforeValidator(get_cmc_date),
]
