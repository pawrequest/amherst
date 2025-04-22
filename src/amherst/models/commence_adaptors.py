from __future__ import annotations

import re
from datetime import date
from enum import StrEnum
from typing import Annotated

import pydantic as _p

from pycommence.pycmc_types import get_cmc_date

LOCATION = 'HM'


class CategoryName(StrEnum):
    Hire = 'Hire'
    Sale = 'Sale'
    Customer = 'Customer'
    Trial = 'Radio Trial'


class ViewCursorName(StrEnum):
    HiresOut = 'Hires Outbound - Paul'
    HiresIn = 'Hires Inbound - Paul'


CursorName = CategoryName | ViewCursorName


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


class SaleStatus(StrEnum):
    BOOKED = 'Ordered Ready To Go'
    PACKED = 'Packed'
    SENT = 'Sent'
    WAITING_PAYMENT = 'Waiting For Payment'
    WAITING_OTHER = 'Waiting For Other'
    WAITING_STOCK = 'Waiting For Stock'
    QUOTE = 'Quote Sent'
    LOST_KIT = 'Lost Kit Invoice'
    CANCELLED = 'Cancelled'
    SUPPLIER = 'Sent Direct From Supplier'


# def get_alias(tablename: str, field_name: str) -> str:
#     match tablename:
#         case 'Hire':
#             return HireAliases[field_name].value()


AM_DATE = Annotated[
    date | None,
    _p.BeforeValidator(get_cmc_date),
]


def addr_in_3_lines(address: str) -> list[str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    return addr_lines


def addrlines(addr_str: str) -> dict[str, str]:
    addr_lines = addr_in_3_lines(addr_str)
    return {f'address_line{num}': line for num, line in enumerate(addr_lines, start=1)}


class EmailOption(_p.BaseModel):
    email: str
    description: str
    name: str

    def __eq__(self, other: EmailOption):
        return self.email == other.email
