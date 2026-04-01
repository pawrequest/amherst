from __future__ import annotations

from abc import ABC
from datetime import date
from os import PathLike
from typing import ClassVar

from loguru import logger
from pycommence.pycmc_types import RowInfo
from pydantic import Field, field_validator
from shipaw.models.address import Address as AddressAgnost
from shipaw.models.address import Contact, FullContact
from shipaw.utils.consts_enums import ShipDirection

from amherst.models.amherst_base import AmherstBase, CommaSeparatedStrField
from amherst.models.commence_adaptors import (
    CategoryName,
    CommenceDate,
    HireStatus,
    SaleStatus,
    replace_noncompliant_apostrophes,
    split_addr_str2,
)
from amherst.models.meta import register_table
from amherst.models.shipment import AmherstShipment


class AmherstShipableBase(AmherstBase, ABC):
    row_info: RowInfo  # commence row info
    # amherst common fieldnames fields
    name: str = Field(..., alias='Name')
    shipped_shipments: CommaSeparatedStrField = Field('', alias='Shipped Shipment')

    # mandatory fields
    customer_name: str
    delivery_contact_name: str
    delivery_contact_business: str
    delivery_contact_phone: str
    delivery_contact_email: str
    delivery_address_str: str
    delivery_address_pc: str

    # optional fields with default
    send_date: CommenceDate = Field(default_factory=date.today)
    booking_date: CommenceDate | None = Field(None, alias='Booked Date')

    boxes: int = Field(default=1, alias='Boxes')

    delivery_method: str | None = None

    @classmethod
    def alias_lookup(cls, field_name: str) -> str:
        try:
            return cls.model_fields[field_name].alias
        except KeyError:
            logger.warning(f'Alias for {field_name} not found in model {cls.__name__}. Returning field name.')
            return field_name

    @field_validator('*', mode='before')
    def preprocess_strings(cls, value):
        return replace_noncompliant_apostrophes(value)

    @field_validator('send_date', mode='after')
    def validate_send_date(cls, v: CommenceDate) -> date:
        if v is None or v < date.today():
            return date.today()
        return v

    @property
    def full_contact(self) -> FullContact:
        addrlines, town = split_addr_str2(self.delivery_address_str)
        return FullContact(
            contact=Contact(
                contact_name=self.delivery_contact_name,
                mobile_phone=self.delivery_contact_phone,
                email_address=self.delivery_contact_email,
            ),
            address=AddressAgnost(
                address_lines=addrlines,
                town=town,
                postcode=self.delivery_address_pc,
                business_name=self.delivery_contact_business,
            ),
        )

    def shipment(self, direction: ShipDirection = ShipDirection.OUTBOUND) -> AmherstShipment:
        return AmherstShipment(
            recipient=self.full_contact,
            boxes=self.boxes,
            shipping_date=self.send_date,
            direction=direction,
            reference=self.customer_name,
            context={'record': self},
        )


class AmherstOrderBase(AmherstShipableBase, ABC):
    # order fields common
    status: str | None = Field(None, alias='Status')
    invoice: PathLike | None = Field(None, alias='Invoice')
    customer_name: str = Field(alias='To Customer')
    order_date: CommenceDate | None = Field(None, alias='Order Date')
    delivery_method: str = Field('', alias='Delivery Method')

    delivery_contact_business: str = Field(alias='Delivery Name')
    delivery_contact_name: str = Field(alias='Delivery Contact')
    delivery_contact_email: str = Field(alias='Delivery Email')
    delivery_contact_phone: str = Field(alias='Delivery Telephone')

    delivery_address_str: str = Field(alias='Delivery Address')
    delivery_address_pc: str = Field(alias='Delivery Postcode')


@register_table
class AmherstCustomer(AmherstShipableBase):
    category: ClassVar[CategoryName] = CategoryName.Customer
    customer_name: str = Field(alias='Name')

    delivery_contact_name: str = Field(alias='Deliv Contact')
    delivery_contact_business: str = Field(alias='Deliv Name')
    delivery_contact_phone: str = Field(alias='Deliv Telephone')
    delivery_contact_email: str = Field(alias='Deliv Email')
    delivery_address_str: str = Field(alias='Deliv Address')
    delivery_address_pc: str = Field(alias='Deliv Postcode')

    # customer fields
    invoice_email: str = Field('', alias='Invoice Email')
    accounts_email: str = Field('', alias='Accounts Email')
    invoice_address_str: str = Field('', alias='Invoice Address')
    invoice_contact: str = Field('', alias='Invoice Contact')
    invoice_name: str = Field('', alias='Invoice Name')
    invoice_postcode: str = Field('', alias='Invoice Postcode')
    invoice_telephone: str = Field('', alias='Invoice Telephone')
    primary_email: str = Field('', alias='Primary Email')
    date_last_contacted: CommenceDate | None = Field(None, alias='Date Last Contact')

    hires: CommaSeparatedStrField = Field('', alias='Has Hired Hires')
    sales: CommaSeparatedStrField = Field('', alias='Involves Sale')


@register_table
class AmherstHire(AmherstOrderBase):
    # optional overrides master
    # aliases: ClassVar[StrEnum] = HireAliases
    category: ClassVar[CategoryName] = CategoryName.Hire

    delivery_contact_phone: str = Field(alias='Delivery Tel')
    delivery_method: str = Field('', alias='Send Method')

    send_date: CommenceDate = Field(default_factory=date.today, alias='Send Out Date')

    # order overides
    status: HireStatus = Field(alias='Status')

    # hire fields
    missing_kit_str: str | None = Field(None, alias='Missing Kit')
    due_back_date: CommenceDate = Field(None, alias='Due Back Date')
    return_notes: str | None = Field(None, alias='Return Notes')
    number_uhf: int = Field(0, alias='Number UHF')
    radio_type: str | None = Field(None, alias='Radio Type')
    number_parrot: int = Field(0, alias='Number Parrot')
    arranged_in: bool = Field(False, alias='Pickup Arranged')
    arranged_out: bool = Field(False, alias='DB label printed')
    pickup_date: CommenceDate | None = Field(None, alias='Pickup Date')


@register_table
class AmherstSale(AmherstOrderBase):
    category: ClassVar[CategoryName] = CategoryName.Sale

    delivery_method: str | None = None

    # optional overrides order
    status: SaleStatus = Field(None, alias='Status')
    booking_date: CommenceDate | None = Field(None, alias='Date Ordered')

    # sale fields
    lost_equipment: str | None = Field(None, alias='Lost Equipment')
    purchase_order: str | None = Field(None, alias='Purchase Order')


@register_table
class AmherstTrial(AmherstOrderBase):
    category: ClassVar[CategoryName] = CategoryName.Trial


AMHERST_ORDER_MODELS = AmherstHire | AmherstSale
SALE_BOOKED_DATE_ALIAS = AmherstSale.alias_lookup('booking_date')
HIRE_SEND_DATE_ALIAS = AmherstHire.alias_lookup('send_date')
HIRE_STATUS_ALIAS = AmherstHire.alias_lookup('status')
HIRE_ALIAS_UHF = AmherstHire.alias_lookup('number_uhf')
HIRE_ALIAS_DUE_BACK = AmherstHire.alias_lookup('due_back_date')
HIRE_ALIAS_RADIO_TYPE = AmherstHire.alias_lookup('radio_type')
HIRE_ALIAS_PARROT = AmherstHire.alias_lookup('number_parrot')
