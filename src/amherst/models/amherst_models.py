# from __future__ import annotations
from __future__ import annotations

from abc import ABC
from datetime import date, datetime
from typing import Annotated

import pydantic as _p
from fastapi.encoders import jsonable_encoder
from loguru import logger
from pydantic import AliasGenerator, BaseModel, ConfigDict

from shipaw.models.pf_shipment import Shipment
from amherst.models.commence_adaptors import (
    AM_DATE,
    AmherstTableName,
    HireStatus,
    customer_alias,
    hire_alias,
    sale_alias,
    trial_alias, SaleStatus,
)
from pycommence.pycmc_types import get_cmc_date
from shipaw.ship_types import limit_daterange_no_weekends

# TableLit = Literal['Hire', 'Sale', 'Customer']
SHIP_DATE = Annotated[
    date,
    _p.BeforeValidator(limit_daterange_no_weekends),
]

AM_SHIP_DATE = Annotated[
    SHIP_DATE,
    _p.BeforeValidator(get_cmc_date),
]


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


class AmherstTableBase(BaseModel, ABC):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    row_id: str | None = None
    name: str
    customer_name: str
    category: AmherstTableName

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

    @property
    def og_address(self):
        return self.address_dict()

    def ship_details_dict(self) -> dict:
        return {
            'total_number_of_parcels': 1,
            'shipping_date': limit_daterange_no_weekends(date.today()),
        }

    def shipment_dict(self):
        return {
            'recipient_address': self.address_dict(),
            'recipient_contact': self.contact_dict(),
            **self.ship_details_dict(),
            **split_refs_from_str(self.customer_name),
        }

    def shipment_pyd(self):
        return Shipment.model_validate(self.shipment_dict())

    def shipment_dict_jsonable(self):
        return jsonable_encoder(self.shipment_dict())

    def jsonable(self) -> dict:
        logger.info('dumping jsonable, why not implement this globally?')
        return jsonable_encoder(self)


class AmherstCustomer(AmherstTableBase):
    model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=customer_alias))
    # model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=customer_alias, )) WHY comma?!
    category: AmherstTableName = 'Customer'
    invoice_email: str = ''
    accounts_email: str = ''
    hires: str = ''
    sales: str = ''


class AmherstTrial(AmherstTableBase):
    model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=trial_alias))
    category: AmherstTableName = 'Trial'
    status: str


class AmherstOrderBase(AmherstTableBase, ABC):
    boxes: int = 1
    invoice: str = ''
    track_out: str = ''
    track_in: str = ''
    arranged_out: bool = False
    arranged_in: bool = False
    delivery_method: str = ''

    send_date: AM_DATE = date.today()

    def ship_details_dict(self) -> dict:
        return {
            'total_number_of_parcels': self.boxes,
            'shipping_date': limit_daterange_no_weekends(self.send_date),
        }


class AmherstSale(AmherstOrderBase):
    category: AmherstTableName = 'Sale'
    model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=sale_alias))
    status: SaleStatus


class AmherstHire(AmherstOrderBase):
    category: AmherstTableName = 'Hire'
    model_config = ConfigDict(alias_generator=AliasGenerator(validation_alias=hire_alias))
    status: HireStatus


AMHERST_ORDER_MODELS = AmherstHire | AmherstSale | AmherstTrial
AMHERST_TABLE_MODELS = AMHERST_ORDER_MODELS | AmherstCustomer


def date_int_w_ordinal(n):
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def dt_ordinal(dt: datetime | date) -> str:
    return dt.strftime(f'%a {date_int_w_ordinal(dt.day)} %b %Y')
    # return dt.strftime('%a {th} %b %Y').replace('{th}', date_int_w_ordinal(dt.day))


def split_refs_from_str(ref_str: str) -> dict[str, str]:
    reference_numbers = {}

    for i in range(1, 6):
        start_index = (i - 1) * 24
        end_index = i * 24
        if start_index < len(ref_str):
            reference_numbers[f'reference_number{i}'] = ref_str[start_index:end_index]
        else:
            break
    return reference_numbers


def add_from_str(add_str: str, postcode: str):
    return {
        **split_addr_str(add_str),
        'postcode': postcode,
    }
