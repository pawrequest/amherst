# from __future__ import annotations
from datetime import date
from enum import Enum
from typing import Annotated

import pydantic as _p
import sqlmodel
from pydantic import BaseModel, ConfigDict, model_validator
from sqlmodel import Relationship, SQLModel

from amherst.commence_adaptors import customer_alias, hire_alias, sale_alias
from amherst.importer import split_refs_from_str
from pycommence.pycmc_types import get_cmc_date
from shipaw.models.pf_shipment import Shipment, to_collection, to_dropoff
from shipaw.ship_types import ShipDirection, limit_daterange_no_weekends

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


class AmherstTableEnum(str, Enum):
    Hire = 'Hire'
    Sale = 'Sale'
    Customer = 'Customer'


class AmherstTableBase(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        validate_default=True,
    )
    # fields for all
    name: str
    category: AmherstTableEnum
    id: str

    customer_name: str

    delivery_contact_name: str
    delivery_contact_business: str
    delivery_contact_phone: str
    delivery_contact_email: str

    delivery_address_str: str
    delivery_address_pc: str
    delivery_address_line1: str | None = None
    delivery_address_line2: str | None = None
    delivery_address_line3: str | None = None
    delivery_town: str | None = None

    # notes
    # reference_number1: str | None = None
    # reference_number2: str | None = None
    # reference_number3: str | None = None
    # reference_number4: str | None = None
    # reference_number5: str | None = None
    # special_instructions1: str | None = None
    # special_instructions2: str | None = None
    # special_instructions3: str | None = None
    # special_instructions4: str | None = None

    # fields for customers
    invoice_email: str = ''
    accounts_email: str = ''

    @model_validator(mode='after')
    def split_address(self):
        if not any([self.delivery_address_line1, self.delivery_address_line2, self.delivery_address_line3]):
            addr_dict = split_addr_str(self.delivery_address_str)
            for key, value in addr_dict.items():
                setattr(self, f'delivery_{key}', value)
        return self

    # @model_validator(mode='after')
    # def split_refs(self):
    #     if not any(
    #             [self.reference_number1, self.reference_number2, self.reference_number3, self.reference_number4,
    #              self.reference_number5]
    #     ):
    #         ref_dict = split_refs_from_str(self.customer_name)
    #         for key, value in ref_dict.items():
    #             setattr(self, key, value)
    #     return self

    @property
    def contact_dict(self) -> dict:
        return {
            'contact_name': self.delivery_contact_name,
            'business_name': self.delivery_contact_business,
            'mobile_phone': self.delivery_contact_phone,
            'email_address': self.delivery_contact_email,
        }

    @property
    def address_dict(self) -> dict:
        return {
            **split_addr_str(self.delivery_address_str),
            'postcode': self.delivery_address_pc,
        }

    @property
    def shipment_dict(self):
        return {
            'recipient_address': self.address_dict,
            'recipient_contact': self.contact_dict,
            'total_number_of_parcels': 1,
            'shipping_date': date.today(),
            **split_refs_from_str(self.name),
        }

    def to_shipment(self, direction: ShipDirection):
        match direction:
            case ShipDirection.Outbound:
                return Shipment.model_validate(self.shipment_dict)
            case ShipDirection.Inbound:
                return to_collection(Shipment.model_validate(self.shipment_dict))
            case ShipDirection.Dropoff:
                return to_dropoff(Shipment.model_validate(self.shipment_dict))
            case _:
                raise ValueError(f'Unknown direction {direction}')


class AmherstOrderBase(AmherstTableBase):
    boxes: int = 1
    send_date: AM_SHIP_DATE = date.today()
    invoice: str = ''
    track_out: str = ''
    track_in: str = ''
    arranged_out: bool = False
    arranged_in: bool = False
    delivery_method: str = ''

    # fields for hires
    missing_kit_str: str = ''

    @property
    def shipment_dict(self):
        return {
            'recipient_address': self.address_dict,
            'recipient_contact': self.contact_dict,
            'total_number_of_parcels': self.boxes,
            'shipping_date': self.send_date,
            **split_refs_from_str(self.name),
        }


class AmherstCustomer(AmherstOrderBase):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=customer_alias
    )


class AmherstCustomerDB(AmherstCustomer, SQLModel, table=True):
    id: str = sqlmodel.Field(primary_key=True)

    hires: list['AmherstHireDB'] = Relationship(back_populates='customer')
    sales: list['AmherstSaleDB'] = Relationship(back_populates='customer')


class AmherstHire(AmherstOrderBase):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=hire_alias
    )


class AmherstHireDB(AmherstHire, SQLModel, table=True):
    id: str = sqlmodel.Field(primary_key=True)
    customer_id: str | None = sqlmodel.Field(foreign_key='amherstcustomerdb.id')
    customer: AmherstCustomerDB | None = Relationship(back_populates='hires')


class AmherstSale(AmherstTableBase):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=sale_alias
    )


class AmherstSaleDB(AmherstSale, SQLModel, table=True):
    id: str = sqlmodel.Field(primary_key=True)

    customer_id: str | None = sqlmodel.Field(foreign_key='amherstcustomerdb.id')
    customer: AmherstCustomerDB = Relationship(back_populates='sales')


class AmherstTableDB(AmherstTableBase, SQLModel, table=True):
    id: str = sqlmodel.Field(primary_key=True)


AMHERST_ORDER_TYPES = AmherstHireDB | AmherstSaleDB
AMHERST_TABLE_TYPES = AMHERST_ORDER_TYPES | AmherstCustomerDB

types_map = {
    'Hire': {
        'input_type': AmherstHire,
        'output_type': AmherstHireDB,
    },
    'Sale': {
        'input_type': AmherstSale,
        'output_type': AmherstSaleDB,
    },
    'Customer': {
        'input_type': AmherstCustomer,
        'output_type': AmherstCustomerDB,
    },
}


def dict_to_amtable(data: dict[str, str]) -> AMHERST_TABLE_TYPES:
    res = types_map[data['category']]['input_type'].model_validate(data)
    tbl = types_map[data['category']]['output_type'](**res.model_dump())
    return tbl
