# from __future__ import annotations
import functools
import typing
from abc import ABC
from copy import copy
from datetime import date
from enum import Enum, StrEnum
from functools import cached_property
from typing import Annotated, Self

import pydantic as _p
from loguru import logger
from pydantic import BaseModel, ConfigDict, Field

from pycommence import PyCommence
from pycommence.pycmc_types import get_cmc_date
from shipaw.ship_types import limit_daterange_no_weekends

AM_DATE = Annotated[
    date,
    _p.BeforeValidator(get_cmc_date),
]

SHIP_DATE = Annotated[
    date,
    _p.BeforeValidator(limit_daterange_no_weekends),
]

AM_SHIP_DATE = Annotated[
    SHIP_DATE,
    _p.BeforeValidator(get_cmc_date),
]


class AmherstTableEnum(StrEnum):
    Hire = 'Hire'
    Sale = 'Sale'
    Customer = 'Customer'


class AmherstTableEnum2(str, Enum):
    Hire = 'Hire'
    Sale = 'Sale'
    Customer = 'Customer'


class AmherstTable(BaseModel, ABC):
    model_config = ConfigDict(
        populate_by_name=True,
        validate_default=True,
    )
    name: str = Field('', alias='Name')
    category: AmherstTableEnum2

    customer_name: str

    contact_contact_name: str
    contact_business_name: str
    contact_mobile_phone: str
    contact_email_address: str

    str_address: str
    address_postcode: str

    shipment_shipping_date: AM_SHIP_DATE = Field(date.today(), alias='Send Out Date')
    shipment_total_number_of_parcels: int = Field(1, alias='Boxes')

    customer_record: Self | None = None

    @_p.model_validator(mode='after')
    def val_customer_record(self):
        if self.customer_record is None:
            self.customer_record = copy(self) if self.category == 'Customer' else get_customer_table(self.customer_name)
        return self

    @cached_property
    def contact_dict(self) -> dict:
        return {k.replace('contact_', '', 1): v for k, v in self.model_dump(exclude={'customer_record'}).items() if
                k.startswith('contact_')}

    @cached_property
    def address_dict(self) -> dict:
        return {
            **addr_town_lines_maybe(self.str_address),
            'postcode': self.address_postcode,
        }

    @cached_property
    def shipment_details(self):
        return {
            k.replace('shipment_', '', 1): v for k, v in self.model_dump(exclude={'customer_record'}).items() if
            k.startswith('shipment_')
        }

    @property
    def shipment_dict(self):
        return {
            'recipient_address': self.address_dict,
            'recipient_contact': self.contact_dict,
            **self.shipment_details
        }


class AmherstCustomerIn(AmherstTable):
    customer_name: str = Field('', alias='Name')

    contact_contact_name: str = Field('', alias='Deliv Contact')
    contact_business_name: str = Field('', alias='Deliv Name')
    contact_mobile_phone: str = Field('', alias='Deliv Tel')
    contact_email_address: str = Field('', alias='Deliv Email')

    str_address: str = Field('', alias='Deliv Address')
    address_postcode: str = Field('', alias='Deliv Postcode')

    invoice_email_address: str = Field('', alias='Invoice Email')
    default_email_address: str = Field('', alias='Default Email')
    accounts_email_address: str = Field('', alias='Accounts Email')


class AmherstOrderIn(AmherstTable):
    customer_name: str = Field('', alias='To Customer')

    contact_contact_name: str = Field('', alias='Delivery Contact')
    contact_business_name: str = Field('', alias='Delivery Name')
    contact_email_address: str = Field('', alias='Delivery Email')
    contact_mobile_phone: str

    str_address: str = Field('', alias='Delivery Address')
    address_postcode: str = Field('', alias='Delivery Postcode')

    delivery_method: str = Field('', alias='Delivery Method')
    arranged_in: bool = Field(False, alias='Pickup Arranged')
    arranged_out: bool = Field(False, alias='DB label printed')
    track_in: str = Field('', alias='Track Inbound')
    track_out: str = Field('', alias='Track Outbound')

    invoice_path: str = Field('', alias='Invoice')


class AmherstHireIn(AmherstOrderIn):
    contact_mobile_phone: str = Field('', alias='Delivery Tel')
    missing_kit_str: str = Field('', alias='Missing Kit')


class AmherstSaleIn(AmherstOrderIn):
    contact_mobile_phone: str = Field('', alias='Delivery Telephone')


def get_am_record(data: dict[str, str]) -> AmherstTable:
    match data['category']:
        case AmherstTableEnum2.Hire:
            return AmherstHireIn.model_validate(data)
        case AmherstTableEnum2.Sale:
            return AmherstSaleIn.model_validate(data)
        case AmherstTableEnum2.Customer:
            return AmherstCustomerIn.model_validate(data)
        case _:
            raise ValueError(f'Unknown table {data['categor']}')


def addr_town_lines_maybe(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    used_lines = [_ for _ in addr_lines if _]
    town = used_lines.pop() if len(used_lines) > 1 else ''
    return {f'address_line{num}': line for num, line in enumerate(used_lines, start=1)} | {'town': town}


@functools.lru_cache
def get_customer_table(customer: str) -> AmherstTable:
    """Get a customer record from `:class:PyCommence`"""
    logger.debug(f'Getting customer record for {customer}')
    try:
        with PyCommence.from_table_name_context(table_name='Customer') as py_cmc:
            rec = py_cmc.one_record(, customer
            rec['category'] = 'Customer'
            return get_am_record(rec)
    except Exception as e:
        logger.error(f'Error getting customer record for {customer}')
        logger.exception(e)
        raise


class AmherstGenericIn(AmherstOrderIn):
    name: str
    category: AmherstTableEnum2

    customer_name: str

    contact_contact_name: str
    contact_business_name: str
    contact_mobile_phone: str
    contact_email_address: str

    str_address: str
    address_postcode: str

    shipment_shipping_date: date
    shipment_total_number_of_parcels: int = 1

    customer_record: typing.Self

    delivery_method: str = ''
    arranged_in: bool = False
    arranged_out: bool = False
    track_in: str = ''
    track_out: str = ''

    invoice_path: str = ''
    missing_kit_str: str = ''

    # invoice_email_address: str
    # default_email_address: str
    # accounts_email_address: str
