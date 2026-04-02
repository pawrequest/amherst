from __future__ import annotations

from datetime import date
from enum import StrEnum
from functools import partial
from pathlib import Path
from typing import Annotated

import pydantic as _p
from pycommence.pycmc_types import (
    RowInfo,
    get_cmc_date,
    to_cmc_date,
)
from pydantic import BeforeValidator, PlainSerializer

# CONSTS

NONCOMPLIANT_APOSTROPHES = ['’', '‘', '′', 'ʼ', '´']


# ENUMS
class RadioType(StrEnum):
    HYTERA = 'Hytera Digital'
    KIRISUN = 'Kirisun UHF'


class CategoryName(StrEnum):
    Shipment = 'Shipment'
    Hire = 'Hire'
    Sale = 'Sale'
    Customer = 'Customer'
    Trial = 'Radio Trial'
    # Repairs = 'Repairs'


class ViewCursorName(StrEnum):
    HiresOut = 'Hires Outbound - Paul'
    HiresIn = 'Hires Inbound - Paul'


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


# Validators etc
def replace_noncompliant_apostrophes(value: str) -> str:
    if isinstance(value, str):
        for char in NONCOMPLIANT_APOSTROPHES:
            value = value.replace(char, "'")
    return value


def split_addr_str2(address: str) -> tuple[list[str], str]:
    addr_lines = address.splitlines()
    town = addr_lines.pop() if len(addr_lines) > 1 else ''

    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
        addr_lines = addr_lines[:3]

    used_lines = [_ for _ in addr_lines if _]
    return used_lines, town


def split_csv(v):
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        v = replace_noncompliant_apostrophes(v)
        return [item.strip() for item in v.split(',') if item.strip()]
    raise ValueError(f'Expected a string, got {type(v)}')


def join_csv(v, separator=', '):
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return separator.join(v)
    raise ValueError(f'Expected a list, got {type(v)}')


join_2lines = partial(join_csv, separator=',\r\n')
join_spaces = partial(join_csv, separator=', ')


# TYPES
class AmherstRowInfo(RowInfo):
    category: CategoryName


CursorName = CategoryName | ViewCursorName

CommenceString = Annotated[str, BeforeValidator(replace_noncompliant_apostrophes)]
CSVLines = Annotated[
    list[str],
    BeforeValidator(split_csv),
    PlainSerializer(join_2lines),
]
CSVSpaces = Annotated[
    list[str],
    BeforeValidator(split_csv),
    PlainSerializer(join_spaces),
]
CommenceDate = Annotated[date | None, _p.BeforeValidator(get_cmc_date), PlainSerializer(to_cmc_date)]
CommencePath = Annotated[Path, BeforeValidator(lambda x: Path(x)), PlainSerializer(str)]
