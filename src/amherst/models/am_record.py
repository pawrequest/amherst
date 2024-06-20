# from __future__ import annotations
import functools
from datetime import date
from enum import StrEnum
from typing import Annotated

import pydantic as _p
import sqlmodel as sqm
from loguru import logger
from pawdantic.pawsql import default_json_field
from pydantic import AliasChoices, ConfigDict, Field

from amherst.commence import CustomerFields
from pycommence import PyCommence
from pycommence.pycmc_types import get_cmc_date
from shipaw.models import pf_lists, pf_models, pf_top
from shipaw.models.pf_models import AddressChoice
from shipaw.models.pf_msg import Alert, Alerts
from shipaw.ship_types import AlertType, limit_daterange_no_weekends

AM_SHIP_DATE = Annotated[
    date,
    Field(date.today(), alias='Send Out Date'),
    _p.BeforeValidator(limit_daterange_no_weekends),
    _p.BeforeValidator(get_cmc_date),
]


class AmherstTableEnum(StrEnum):
    Hire = 'Hire'
    Sale = 'Sale'
    Customer = 'Customer'


class AmherstRecordIn(sqm.SQLModel):
    model_config = ConfigDict(
        populate_by_name=True,
        validate_default=True,
    )
    cmc_table_name: AmherstTableEnum
    alerts: Alerts = default_json_field(Alerts, Alerts.empty)
    # alerts: list[Alert] | None = optional_json_field(Alert)
    name: str = Field(..., alias='Name')
    customer: str = Field(..., validation_alias=AliasChoices('To Customer', 'Name'))
    send_date: AM_SHIP_DATE
    delivery_contact: str = Field(..., validation_alias=AliasChoices('Delivery Contact', 'Deliv Contact'))
    delivery_business: str = Field(
        ..., validation_alias=AliasChoices('Delivery Name', 'Deliv Name', 'Customer', 'To Customer')
    )
    telephone: str = Field(..., validation_alias=AliasChoices('Delivery Tel', 'Deliv Telephone', 'Delivery Telephone'))
    email: str = Field('', validation_alias=AliasChoices('Delivery Email', 'Deliv Email'))
    address_str: str = Field(..., validation_alias=AliasChoices('Delivery Address', 'Deliv Address'))

    postcode: str = Field(..., validation_alias=AliasChoices('Delivery Postcode', 'Deliv Postcode'))
    send_method: str = Field('', validation_alias=AliasChoices('Send Method', 'Delivery Method'))
    invoice_path: str | None = Field(None, validation_alias=AliasChoices('Invoice', 'Invoice Path'))
    missing_kit_str: str | None = Field(None, alias='Missing Kit')
    boxes: int = Field(1, alias='Boxes')
    track_in: str | None = Field(None, alias='Track Inbound')
    track_out: str | None = Field(None, alias='Track Outbound')
    address_choice: AddressChoice | None = None

    # def get_cmc_update(self, direction:ShipDirection) -> dict[str, str]:
    #     match direction:
    #         case 'out':
    #             return {
    #                 tracking_link_field: tracking_link,
    #                 HireFields.DB_LABEL_PRINTED: True
    #             }

    @functools.cached_property
    def email_options(self):
        email_dict = {
            self.customer_record().get(CustomerFields.ACCOUNTS_EMAIL): ('accounts', 'Customer Accounts'),
            self.customer_record().get(CustomerFields.PRIMARY_EMAIL): ('primary', 'Customer Primary'),
            self.customer_record().get(CustomerFields.DELIVERY_EMAIL): ('cust_del', 'Customer Default Delivery'),
            self.customer_record().get(CustomerFields.INVOICE_EMAIL): ('invoice', 'Customer Invoice'),
            self.email: ('rec_del', f'{self.cmc_table_name.title()} Delivery'),
        }
        options = [
            EmailOption(name=name, email=email, description=description)
            for email, (name, description) in email_dict.items()
            if email
        ]
        return options

    def customer_record(self) -> dict[str, str]:
        return self.model_dump() if self.cmc_table_name == 'Customer' else get_customer_record(self.customer)

    @property
    def input_address(self):
        return pf_models.AddressRecipient(
            **addr_town_lines_maybe(self.address_str),
            postcode=self.postcode,
        )

    def contact(self) -> pf_top.Contact | pf_top.ContactTemporary:
        contact_dict = dict(
            business_name=self.delivery_business,
            email_address=self.email,
            mobile_phone=self.telephone,
            contact_name=self.delivery_contact,
            notifications=pf_lists.RecipientNotifications.standard_recip(),
        )
        try:
            contact_model = pf_top.Contact(**contact_dict)
            contact_model.model_validate(contact_model)
        except _p.ValidationError as err:
            errors = err.errors()
            reasons = [_.get('ctx').get('reason') for _ in errors]
            err_msg = ', '.join(reasons)
            logger.warning(err_msg)
            contact_model = pf_top.ContactTemporary(**contact_dict)
            self.alerts.alert.append(Alert(type=AlertType.ERROR, message=err_msg))
        return contact_model

    def missing_kit(self) -> list[str] | None:
        return self.missing_kit_str.splitlines() if self.missing_kit_str else None


class AmherstRecord(AmherstRecordIn):
    send_date: date


# def initial_shipment_state(self) -> Shipment:
#     try:
#         el_client = ELClient()
#         chosen = el_client.choose_address(self.input_address())
#         return Shipment(
#             contact=self.contact(),
#             address=chosen,
#             ship_date=self.send_date,
#             boxes=self.boxes,
#             reference_number1=self.customer,
#         )
#     except BackendError as err:
#         logger.exception(
#             f'Zeep Backend Error prevents retrieving initial state for {self.name}:{str(err)}'
#         )
#         raise


# class AmherstRecordDB(AmherstRecord, table=True):
#     id: int | None = sqm.Field(primary_key=True)
#     booking_states: list['BookingStateDB'] = sqm.Relationship(
#         back_populates="record",
#     )


def addr_lines_dict_am(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    return {f'address_line{num}': line for num, line in enumerate(addr_lines, start=1)}


def addr_town_lines_maybe(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    used_lines = [_ for _ in addr_lines if _]
    town = used_lines.pop() if len(used_lines) > 1 else ''
    return {f'address_line{num}': line for num, line in enumerate(used_lines, start=1)} | {'town': town}


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


class EmailOption(_p.BaseModel):
    email: str
    description: str
    name: str

    def __eq__(self, other: 'EmailOption'):
        return self.email == other.email
