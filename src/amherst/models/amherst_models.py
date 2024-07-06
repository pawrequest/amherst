# from __future__ import annotations
from __future__ import annotations

from abc import ABC
from datetime import date, datetime
from enum import Enum
from typing import Annotated, Literal

import pydantic as _p
from pydantic import AliasGenerator, BaseModel, ConfigDict

from amherst.models.commence_adaptors import (
    AM_DATE,
    HireStatus,
    customer_alias,
    hire_alias,
    sale_alias,
)
from pycommence.pycmc_types import get_cmc_date
from shipaw.ship_types import limit_daterange_no_weekends

SHIP_DATE = Annotated[
    date,
    _p.BeforeValidator(limit_daterange_no_weekends),
]

AM_SHIP_DATE = Annotated[
    SHIP_DATE,
    _p.BeforeValidator(get_cmc_date),
]


def constrain_date(datestr):
    datey = get_cmc_date(datestr)
    datey2 = limit_daterange_no_weekends(datey)
    return datey2


def split_addr_str(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
        addr_lines = addr_lines[:3]

    used_lines = [_ for _ in addr_lines if _]
    town = used_lines.pop() if len(used_lines) > 1 else ''
    return {f'address_line{num}': line for num, line in enumerate(used_lines, start=1)} | {'town': town}


class AmherstTableEnum(str, Enum):
    Hire = 'Hire'
    Sale = 'Sale'
    Customer = 'Customer'


TABLE_LITERAL = Literal['Hire', 'Sale', 'Customer']


class AmherstTableBase(BaseModel, ABC):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    row_id: str | None = None
    name: str
    category: TABLE_LITERAL

    delivery_contact_name: str
    delivery_contact_business: str
    delivery_contact_phone: str
    delivery_contact_email: str

    delivery_address_str: str
    delivery_address_pc: str

    @staticmethod
    def dt_ordinal(date_or_dt: datetime | date) -> str:
        return dt_ordinal(date_or_dt)

    def contact_dict(self) -> dict:
        return {
            'contact_name': self.delivery_contact_name,
            'business_name': self.delivery_contact_business,
            'mobile_phone': self.delivery_contact_phone,
            'email_address': self.delivery_contact_email,
        }

    def address_dict(self) -> dict:
        return {
            **split_addr_str(self.delivery_address_str),
            'postcode': self.delivery_address_pc,
        }

    def ship_details_dict(self):
        return {
            'total_number_of_parcels': 1,
            'shipping_date': limit_daterange_no_weekends(date.today()),
        }

    def shipment_dict(self):
        return {
            'recipient_address': self.address_dict(),
            'recipient_contact': self.contact_dict(),
            **self.ship_details_dict(),
            **split_refs_from_str(self.name),
        }


class AmherstCustomer(AmherstTableBase):
    model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=customer_alias, ))
    category: TABLE_LITERAL = 'Customer'
    invoice_email: str = ''
    accounts_email: str = ''


class AmherstOrderBase(AmherstTableBase, ABC):
    customer_name: str
    invoice: str = ''
    track_out: str = ''
    track_in: str = ''
    arranged_out: bool = False
    arranged_in: bool = False
    delivery_method: str = ''

    send_date: AM_DATE = date.today()


class AmherstSale(AmherstOrderBase):
    model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=sale_alias))
    category: TABLE_LITERAL = 'Sale'


class AmherstHire(AmherstOrderBase):
    model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=hire_alias))
    boxes: int = 1
    status: HireStatus
    category: TABLE_LITERAL = 'Hire'
    send_date: AM_DATE = None

    @property
    def ship_details_dict(self):
        return {
            'total_number_of_parcels': self.boxes,
            'shipping_date': limit_daterange_no_weekends(self.send_date),
        }


AMHERST_ORDER_TYPES = AmherstHire | AmherstSale
AMHERST_TABLE_TYPES = AMHERST_ORDER_TYPES | AmherstCustomer


def date_int_w_ordinal(n):
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def dt_ordinal(dt: datetime | date) -> str:
    return dt.strftime(f'%a {date_int_w_ordinal(dt.day)} %b')
    # return dt.strftime('%a {th} %b %Y').replace('{th}', date_int_w_ordinal(dt.day))


def split_refs_from_str(customer_str: str) -> dict[str, str]:
    reference_numbers = {}

    for i in range(1, 6):
        start_index = (i - 1) * 24
        end_index = i * 24
        if start_index < len(customer_str):
            reference_numbers[f'reference_number{i}'] = customer_str[start_index:end_index]
        else:
            break
    return reference_numbers
