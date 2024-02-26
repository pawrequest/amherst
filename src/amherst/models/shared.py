from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel

from pycommence import CmcFilter, FilterArray
from pycommence.api import entities as ent
from pycommence.api.filters import FilterCondition

SALE_CUSTOMERS = ent.Connection(
    name='SaleCustomers',
    to_table='Customers',
    from_table='Sale',
)

HIRE_CUSTOMERS = ent.Connection(
    name='HireCustomers',
    to_table='Customers',
    from_table='Hire',
)


class ContactAm(BaseModel):
    email: str
    name: str
    telephone: str

#
# class AddressAm(BaseModel):
#     # todo separate contact
#     address: str
#     contact: str
#     email: str
#     postcode: str
#     telephone: str
#
#     @property
#     def addr_lines(self) -> list[str]:
#         addr_lines = self.address.splitlines()
#         if len(addr_lines) < 3:
#             addr_lines.extend([''] * (3 - len(addr_lines)))
#         elif len(addr_lines) > 3:
#             addr_lines[2] = ','.join(addr_lines[2:])
#         return addr_lines
#
#     @property
#     def addr_lines_dict(self) -> dict[str, str]:
#         addr_lines = self.address.splitlines()
#         if len(addr_lines) < 3:
#             addr_lines.extend([''] * (3 - len(addr_lines)))
#         elif len(addr_lines) > 3:
#             addr_lines[2] = ','.join(addr_lines[2:])
#         return {
#             f'address_line{num}': line
#             for num, line in enumerate(addr_lines, start=1)
#         }


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
    filters=
    {
        1: CmcFilter(
            field_name='Status',
            condition=FilterCondition.EQUAL_TO,
            value=HireStatusEnum.BOOKED_IN,
        ),
        2: CmcFilter(
            field_name='Send Out Date',
            condition=FilterCondition.AFTER,
            value='2023-01-01',
        ),
    }
)

INITIAL_FILTER_ARRAY2 = FilterArray().add_filters(
    CmcFilter(
        field_name='Status',
        condition=FilterCondition.EQUAL_TO,
        value=HireStatusEnum.BOOKED_IN,
    ),
    CmcFilter(
        field_name='Send Out Date',
        condition=FilterCondition.AFTER,
        value='2023-01-01',
    ),
)


class AmherstFields(StrEnum):
    ACTUAL_RETURN_DATE = 'Actual Return Date'
    ADDRESS = 'Delivery Address'
    AERIAL_ADAPT = 'Number Aerial Adapt'
    ALL_ADDRESS = 'All Address'
    BATTERIES = 'Number Batteries'
    BOOKED_DATE = 'Booked Date'
    BOXES = 'Boxes'
    BUSINESS_NAME = 'Delivery Name'
    CASES = 'Number Cases'
    CLIPON_AERIAL = 'Number Clipon Aerial'
    CLOSED = 'Closed'
    CONTACT = 'Delivery Contact'
    CUSTOMER = 'To Customer'
    DB_LABEL_PRINTED = 'DB label printed'
    DELIVERY_COST = 'Delivery Cost'
    DISCOUNT_DESCRIPTION = 'Discount Description'
    DISCOUNT_PERCENTAGE = 'Discount Percentage'
    DUE_BACK_DATE = 'Due Back Date'
    EM = 'Number EM'
    EMAIL = 'Delivery Email'
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
    POSTCODE = 'Delivery Postcode'
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
    TELEPHONE = 'Delivery Tel'
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
