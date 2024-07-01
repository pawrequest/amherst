# from __future__ import annotations
from datetime import date
from enum import Enum
from typing import Annotated

import pydantic as _p
import sqlmodel
from pydantic import BaseModel, ConfigDict
from sqlmodel import SQLModel

from amherst.commence_adaptors import get_customer_alias, get_hire_alias, get_sale_alias
from amherst.importer import split_addr_str
from amherst.models.db_models import BookingStateDB
from pycommence.pycmc_types import get_cmc_date
from shipaw.models.pf_shipment import Shipment, to_collection, to_dropoff
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
    row_id: str

    customer_name: str = ''

    delivery_contact_name: str
    delivery_contact_business: str
    delivery_contact_phone: str
    delivery_contact_email: str

    delivery_address_str: str
    delivery_address_pc: str

    # fields for customers
    invoice_email: str = ''
    accounts_email: str = ''

    # fields for orders
    boxes: int = 1
    send_date: SHIP_DATE = date.today()
    invoice: str = ''
    track_out: str = ''
    track_in: str = ''
    arranged_out: bool = False
    arranged_in: bool = False
    delivery_method: str = ''

    # fields for hires
    missing_kit_str: str = ''

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
            'total_number_of_parcels': self.boxes,
            'shipping_date': self.send_date,
        }

    def to_outbound(self):
        return Shipment.model_validate(self.shipment_dict)

    def to_inbound(self):
        ship = Shipment.model_validate(self.shipment_dict)
        return to_collection(ship)

    def to_dropoff(self):
        ship = Shipment.model_validate(self.shipment_dict)
        return to_dropoff(ship)


class AmherstCustomerIn(AmherstTableBase):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=get_customer_alias
    )


class AmherstHireIn(AmherstTableBase):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=get_hire_alias
    )


class AmherstSaleIn(AmherstTableBase):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=get_sale_alias
    )


class AmherstTableDB(AmherstTableBase, SQLModel, table=True):
    row_id: str = sqlmodel.Field(primary_key=True)


def get_am_record_smpl(data: dict[str, str]) -> AmherstTableDB:
    match data['category']:
        case AmherstTableEnum.Hire:
            res = AmherstHireIn.model_validate(data)
        case AmherstTableEnum.Sale:
            res = AmherstSaleIn.model_validate(data)
        case AmherstTableEnum.Customer:
            res = AmherstCustomerIn.model_validate(data)
        case _:
            raise ValueError(f'Unknown table {data['categor']}')
    return AmherstTableDB.model_validate(res, from_attributes=True)


def amrec_booking(amrec: AmherstTableDB):
    bk = {'shipment_request': amrec.shipment_dict}
    return BookingStateDB.model_validate(bk)
