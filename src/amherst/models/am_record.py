# from __future__ import annotations
from datetime import date
from enum import StrEnum
import functools
import typing as _t
from pathlib import Path

import sqlmodel as sqm
import pydantic as _p
from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field
from combadge.core.errors import BackendError
from loguru import logger

from amherst.am_shared import CustomerFields
from pycommence import PyCommence, pycmc_types
from shipaw import ELClient, Shipment
from shipaw.models import pf_lists, pf_models, pf_top
from shipaw.ship_types import SHIPPING_DATE

AmherstTableName = _t.Literal['Hire', 'Sale', 'Customer']
CMC_SHIP_DATE2 = _t.Annotated[SHIPPING_DATE, _p.BeforeValidator(pycmc_types.get_cmc_date)]


class AmherstTableEnum(StrEnum):
    Hire = 'Hire'
    Sale = 'Sale'
    Customer = 'Customer'


class AmherstRecord(sqm.SQLModel):
    model_config = ConfigDict(
        populate_by_name=True,
    )
    cmc_table_name: AmherstTableEnum

    name: str = Field(..., alias='Name')
    customer: str = Field(..., validation_alias=AliasChoices('To Customer', 'Name'))
    send_date: date = Field(date.today(), alias='Send Out Date')
    delivery_contact: str = Field(
        ...,
        validation_alias=AliasChoices('Delivery Contact', 'Deliv Contact')
    )
    delivery_business: str = Field(
        ..., validation_alias=AliasChoices('Delivery Name', 'Deliv Name', 'Customer', 'To Customer')
    )
    telephone: str = Field(
        ...,
        validation_alias=AliasChoices('Delivery Tel', 'Deliv Telephone', 'Delivery Telephone')
    )
    email: _p.EmailStr = Field(..., validation_alias=AliasChoices('Delivery Email', 'Deliv Email'))
    address_str: str = Field(
        ...,
        validation_alias=AliasChoices('Delivery Address', 'Deliv Address')
    )
    postcode: str = Field(..., validation_alias=AliasChoices('Delivery Postcode', 'Deliv Postcode'))
    send_method: str = Field('', validation_alias=AliasChoices('Send Method', 'Delivery Method'))
    invoice_path: str | None = Field(None, validation_alias=AliasChoices('Invoice', 'Invoice Path'))
    missing_kit_str: str | None = Field(None, alias='Missing Kit')
    boxes: int = Field(1, alias='Boxes')
    track_in: str | None = Field(None, alias='Track Inbound')
    track_out: str | None = Field(None, alias='Track Outbound')

    @_p.field_validator('send_date', mode='before')
    def cmc_date(cls, v):
        if isinstance(v, str):
            if len(v) == 8:
                return pycmc_types.get_cmc_date(v)
            raise ValueError('Date must be in format YYYYMMDD')
        return v

    def email_options(self):
        maybes = [
            dict(
                name='accounts',
                email=self.customer_record().get(CustomerFields.ACCOUNTS_EMAIL),
                description='Customer Accounts'
            ),
            dict(
                name='primary',
                email=self.customer_record().get(CustomerFields.PRIMARY_EMAIL),
                description='Customer Primary'
            ),
            dict(
                name='cust_del',
                email=self.customer_record().get(CustomerFields.DELIVERY_EMAIL),
                description='Customer Default Delivery'
            ),
            dict(
                name='invoice',
                email=self.customer_record().get(CustomerFields.INVOICE_EMAIL),
                description='Customer Invoice'
            ),
            dict(
                name='rec_del',
                email=self.email,
                description=f'{self.cmc_table_name.title()} Delivery'
            )
        ]

        return [EmailOption(**i) for i in maybes if i['email']]

    def email_addresses(self):
        maybe_emails = [
            self.customer_record().get(CustomerFields.ACCOUNTS_EMAIL),
            self.customer_record().get(CustomerFields.PRIMARY_EMAIL),
            self.customer_record().get(CustomerFields.DELIVERY_EMAIL),
            self.customer_record().get(CustomerFields.INVOICE_EMAIL),
            self.email,
        ]
        return [i for i in maybe_emails if i]

    # @_p.field_validator('send_date', mode='after')
    # def date_not_past(cls, v, info):
    #     tod = datetime.date.today()
    #     return v if v >= tod else tod

    @functools.lru_cache()
    def customer_record(self) -> dict[str, str]:
        return self.model_dump() if self.cmc_table_name == 'Customer' else get_customer_record(
            self.customer
        )

    def input_address(self):
        return pf_models.AddressRecipient(
            **addr_lines_dict_am(self.address_str),
            town='',
            postcode=self.postcode,
        )

    def contact(self):
        return pf_top.Contact(
            business_name=self.delivery_business,
            email_address=self.email,
            mobile_phone=self.telephone,
            contact_name=self.delivery_contact,
            notifications=pf_lists.RecipientNotifications.standard_recip(),
        )

    def missing_kit(self) -> list[str] | None:
        return self.missing_kit_str.splitlines() if self.missing_kit_str else None

    def initial_shipment_state(self) -> Shipment:
        try:
            el_client = ELClient()
            chosen = el_client.choose_address(self.input_address())
            return Shipment(
                contact=self.contact(),
                address=chosen,
                ship_date=self.send_date,
                boxes=self.boxes,
                reference_number1=self.customer,
            )
        except BackendError as err:
            logger.exception(
                f'Zeep Backend Error prevents retrieving initial state for {self.name}:{str(err)}'
            )
            raise


class AmherstRecordDB(AmherstRecord, table=True):
    id: int | None = sqm.Field(primary_key=True)


def addr_lines_dict_am(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    return {f'address_line{num}': line for num, line in enumerate(addr_lines, start=1)}


def get_email(fields_enum, record):
    return (
            record.get(fields_enum.DELIVERY_EMAIL)
            or record.get(fields_enum.PRIMARY_EMAIL)
            or r'EMAIL_NOT_FOUND@FILLMEIN.COM'
    )


@functools.lru_cache
def get_customer_record(customer: str) -> dict[str, str]:
    """Get a customer record from `:class:PyCommence`"""
    logger.debug(f'Getting customer record for {customer}')
    with PyCommence.from_table_name_context(table_name='Customer') as py_cmc:
        rec = py_cmc.one_record(customer)
    # py_cmc = PyCommence.from_table_name(table_name='Customer')
    # rec = py_cmc.one_record(customer)
    return rec


# class AmherstRecordPartial(AmherstRecord):
#     delivery_contact: str = Field(
#         '',
#         validation_alias=AliasChoices('Delivery Contact', 'Deliv Contact')
#     )
#     delivery_business: str = Field(
#         '',
#         validation_alias=AliasChoices('Delivery Name', 'Deliv Name', 'Customer', 'To Customer')
#     )
#     telephone: str = Field(
#         '',
#         validation_alias=AliasChoices('Delivery Tel', 'Deliv Telephone', 'Delivery Telephone')
#     )
#     email: str = Field('', validation_alias=AliasChoices('Delivery Email', 'Deliv Email'))
#     address_str: str = Field(
#         '',
#         validation_alias=AliasChoices('Delivery Address', 'Deliv Address')
#     )
#     postcode: str = Field('', validation_alias=AliasChoices('Delivery Postcode', 'Deliv Postcode'))
#
#     @field_validator('email', mode='after')
#     def fake_email(cls, v, values):
#         if not v:
#             return "THISEMAILNOTREAL@REPLACEME.com"
#         return v


class EmailOption(BaseModel):
    email: EmailStr
    description: str
    name: str

    def __eq__(self, other: 'EmailOption'):
        return self.email == other.email
