import datetime
import datetime as dt
import typing as _t
from pathlib import Path

import pydantic as _p
import sqlmodel as sqm
from loguru import logger
from pydantic import AliasChoices, Field

import pycommence
from pycommence import pycmc_types
from shipaw import ShipStatePartial, ship_types
from shipaw.models import base_item, pf_ext, pf_lists, pf_top, shipable
from shipaw.ship_ui.states import ShipStateExtra
from amherst.am_types import AmherstFieldsEnumType, AmherstTableName
from amherst.models import am_shared


class ShipableItem(base_item.BaseItem):
    """A shipable item

    Attributes:
        cmc_table_name (AmherstTableName): The name of the table in Commence
        record (dict[str, str]): The record from Commence

        boxes (int | None): The number of boxes
        ship_date (dt.date | None): The date to ship
        name (str | None): The name of the item
        input_address (pf_ext.AddressRecipient | None): The address to ship to
        contact (pf_top.Contact | None): The contact to ship to
        fields_enum (type[AmherstFieldsEnumType]): The fields enum for the table
        customer_record (dict[str, str] | None): The customer record

    """

    cmc_table_name: AmherstTableName
    record: dict[str, str] = sqm.Field(sa_column=sqm.Column(sqm.JSON))

    boxes: int | None = None
    ship_date: dt.date | None = None
    name: str | None = None
    input_address: pf_ext.AddressRecipient | None = None
    contact: pf_top.Contact | None = None
    fields_enum: type[AmherstFieldsEnumType] = _p.Field(default=None, exclude=True)
    customer_record: dict[str, str] | None = _p.Field(default=None, sa_column=sqm.Column(sqm.JSON))

    @_p.model_validator(mode='after')
    def get_values(self):
        self.fields_enum = self.fields_enum or getattr(am_shared, self.cmc_table_name + 'Fields')
        if self.cmc_table_name == 'Customer':
            self.customer_record = self.record
            business_name = self.record.get(self.fields_enum.NAME)
        else:
            business_name = self.record.get(self.fields_enum.CUSTOMER)
            self.customer_record = get_customer_record(customer=business_name)

        self.boxes = int(self.record.get(self.fields_enum.BOXES, 1))
        ship_date = self.record.get(self.fields_enum.SEND_OUT_DATE)
        self.ship_date = pycmc_types.get_cmc_date(ship_date) if ship_date else dt.date.today()
        phone = self.record.get(self.fields_enum.DELIVERY_TELEPHONE)
        email = (
            self.record.get(self.fields_enum.DELIVERY_EMAIL)
            or self.customer_record.get(self.fields_enum.PRIMARY_EMAIL)
            or r'EMAIL_NOT_FOUND@FILLMEIN.COM'
        )
        contact_name = self.record.get(self.fields_enum.DELIVERY_CONTACT)
        postcode = self.record.get(self.fields_enum.DELIVERY_POSTCODE)
        address_str = (
            self.record.get(self.fields_enum.DELIVERY_ADDRESS)
            or self.customer_record.get(am_shared.CustomerFields.DELIVERY_ADDRESS)
            or self.customer_record.get(am_shared.CustomerFields.INVOICE_ADDRESS)
        )

        self.contact = pf_top.Contact(
            business_name=business_name,
            email_address=email,
            mobile_phone=phone,
            contact_name=contact_name,
            notifications=pf_lists.RecipientNotifications.standard_recip(),
        )
        self.name = self.record.get(am_shared.HireFields.NAME)
        self.input_address = pf_ext.AddressRecipient(
            **am_shared.addr_lines_dict_am(address_str),
            town='',
            postcode=postcode,
        )

        return self


def record_to_state(record: dict[str, str], cmc_table_name) -> ShipStatePartial:
    fields_enum = getattr(am_shared, cmc_table_name + 'Fields')
    state = ShipStatePartial()

    business_name = record.get(fields_enum.CUSTOMER)
    ship_date = record.get(fields_enum.SEND_OUT_DATE)
    phone = record.get(fields_enum.DELIVERY_TELEPHONE)
    email = get_email(fields_enum, record)
    contact_name = record.get(fields_enum.DELIVERY_CONTACT)
    postcode = record.get(fields_enum.DELIVERY_POSTCODE)
    address_str = record.get(fields_enum.DELIVERY_ADDRESS)

    state.ship_date = pycmc_types.get_cmc_date(ship_date) if ship_date else dt.date.today()
    state.boxes = int(record.get(fields_enum.BOXES, 1))
    state.contact = pf_top.Contact(
        business_name=business_name,
        email_address=email,
        mobile_phone=phone,
        contact_name=contact_name,
        notifications=pf_lists.RecipientNotifications.standard_recip(),
    )
    state.input_address = (
        pf_ext.AddressRecipient(
            **am_shared.addr_lines_dict_am(address_str),
            town='',
            postcode=postcode,
        )
        if address_str
        else None
    )

    return state


def get_email(fields_enum, record):
    return (
        record.get(fields_enum.DELIVERY_EMAIL)
        or record.get(fields_enum.PRIMARY_EMAIL)
        or r'EMAIL_NOT_FOUND@FILLMEIN.COM'
    )


def get_customer_record(customer: str) -> dict[str, str]:
    """Get a customer record from `:class:PyCommence`"""
    logger.debug(f'Getting customer record for {customer}')
    py_cmc = pycommence.PyCommence.from_table_name(table_name='Customer')
    rec = py_cmc.one_record(customer)
    return rec


CMC_SHIP_DATE2 = _t.Annotated[ship_types.SHIPPING_DATE, _p.BeforeValidator(pycmc_types.get_cmc_date)]


class ShipableRecord(shipable.Shipable):
    cmc_table_name: AmherstTableName = Field(..., alias='Cmc Table Name')
    customer: str = Field(..., validation_alias=AliasChoices('To Customer', 'Name'))
    ship_date: CMC_SHIP_DATE2 = Field(datetime.date.today(), alias='Send Out Date')
    delivery_contact: str = Field(..., validation_alias=AliasChoices('Delivery Contact', 'Deliv Contact'))
    delivery_business: str = Field(
        ..., validation_alias=AliasChoices('Delivery Name', 'Deliv Name', 'Customer', 'To Customer')
    )
    telephone: str = Field(..., validation_alias=AliasChoices('Delivery Tel', 'Deliv Telephone', 'Delivery Telephone'))
    email: _p.EmailStr = Field(..., validation_alias=AliasChoices('Delivery Email', 'Deliv Email'))
    address_str: str = Field(..., validation_alias=AliasChoices('Delivery Address', 'Deliv Address'))
    postcode: str = Field(..., validation_alias=AliasChoices('Delivery Postcode', 'Deliv Postcode'))
    send_method: str = Field('', validation_alias=AliasChoices('Send Method', 'Delivery Method'))
    invoice: Path | None = Field(None, validation_alias=AliasChoices('Invoice', 'Invoice Path'))
    missing_kit_str: str | None = Field(None, alias='Missing Kit')

    @property
    def missing_kit(self) -> list[str] | None:
        return self.missing_kit_str.splitlines() if self.missing_kit_str else None

    @property
    def address(self):
        return pf_ext.AddressRecipient(
            **am_shared.addr_lines_dict_am(self.address_str),
            town='',
            postcode=self.postcode,
        )

    @property
    def contact(self):
        return pf_top.Contact(
            business_name=self.delivery_business,
            email_address=self.email,
            mobile_phone=self.telephone,
            contact_name=self.delivery_contact,
            notifications=pf_lists.RecipientNotifications.standard_recip(),
        )

    @property
    def ship_state(self):
        return ShipStateExtra.model_validate(self, from_attributes=True)
