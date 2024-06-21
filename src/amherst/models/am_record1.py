# # from __future__ import annotations
# from datetime import date, datetime
# from enum import StrEnum
# import functools
# from typing import Annotated
#
# import sqlmodel as sqm
# import pydantic as _p
# from pawdantic.pawsql import optional_json_field
# from pydantic import AliasChoices, ConfigDict, EmailStr, Field
# from loguru import logger
#
# from amherst.am_shared import CustomerFields
# from pycommence import PyCommence
# from pycommence.pycmc_types import get_cmc_date
# from shipaw.models import pf_lists, pf_models, pf_top
# from shipaw.models.pf_msg import Alert
# from shipaw.ship_types import limit_daterange_no_weekends, AlertType
#
#
# class AmherstTableEnum(StrEnum):
#     Hire = 'Hire'
#     Sale = 'Sale'
#     Customer = 'Customer'
#
#
# class AmherstRecord(sqm.SQLModel):
#     model_config = ConfigDict(
#         populate_by_name=True,
#     )
#     cmc_table_name: AmherstTableEnum
#     alerts: list[Alert] | None = optional_json_field(Alert)
#     name: str = Field(..., alias='Name')
#     customer: str = Field(..., validation_alias=AliasChoices('To Customer', 'Name'))
#     send_date: Annotated[
#         date, Field(datetime.today(), alias='Send Out Date'), _p.BeforeValidator(
#             get_cmc_date
#         ), _p.AfterValidator(limit_daterange_no_weekends)]
#     delivery_contact: str = Field(
#         ...,
#         validation_alias=AliasChoices('Delivery Contact', 'Deliv Contact')
#     )
#     delivery_business: str = Field(
#         ..., validation_alias=AliasChoices('Delivery Name', 'Deliv Name', 'Customer', 'To Customer')
#     )
#     telephone: str = Field(
#         ...,
#         validation_alias=AliasChoices('Delivery Tel', 'Deliv Telephone', 'Delivery Telephone')
#     )
#     email: str = Field(..., validation_alias=AliasChoices('Delivery Email', 'Deliv Email'))
#     address_str: str = Field(
#         ...,
#         validation_alias=AliasChoices('Delivery Address', 'Deliv Address')
#     )
#
#     postcode: str = Field(..., validation_alias=AliasChoices('Delivery Postcode', 'Deliv Postcode'))
#     send_method: str = Field('', validation_alias=AliasChoices('Send Method', 'Delivery Method'))
#     invoice_path: str | None = Field(None, validation_alias=AliasChoices('Invoice', 'Invoice Path'))
#     missing_kit_str: str | None = Field(None, alias='Missing Kit')
#     total_number_of_parcels: int = Field(1, alias='Boxes')
#     track_in: str | None = Field(None, alias='Track Inbound')
#     track_out: str | None = Field(None, alias='Track Outbound')
#
#     @functools.cached_property
#     def email_options(self):
#         email_dict = {
#             self.customer_record().get(CustomerFields.ACCOUNTS_EMAIL): ('accounts',
#                                                                         'Customer Accounts'),
#             self.customer_record().get(CustomerFields.PRIMARY_EMAIL): ('primary',
#                                                                        'Customer Primary'),
#             self.customer_record().get(CustomerFields.DELIVERY_EMAIL): ('cust_del',
#                                                                         'Customer Default Delivery'),
#             self.customer_record().get(CustomerFields.INVOICE_EMAIL): ('invoice',
#                                                                        'Customer Invoice'),
#             self.email: ('rec_del', f'{self.cmc_table_name.title()} Delivery')
#
#         }
#         options = [EmailOption(name=name, email=email, description=description) for
#                    email, (name, description) in email_dict.items() if email]
#         return options
#
#     def customer_record(self) -> dict[str, str]:
#         return self.model_dump() if self.cmc_table_name == 'Customer' else get_customer_record(
#             self.customer
#         )
#
#     def input_address(self):
#         return pf_models.AddressRecipient(
#             **addr_town_lines_maybe(self.address_str),
#             postcode=self.postcode,
#         )
#
#     #
#     # def input_address(self):
#     #     return pf_models.AddressRecipient(
#     #         **addr_lines_dict_am(self.address_str),
#     #         town='',
#     #         postcode=self.postcode,
#     #     )
#
#     def contact(self) -> pf_top.Contact | pf_top.ContactTemporary:
#         contact_dict = dict(
#             business_name=self.delivery_business,
#             email_address=self.email,
#             mobile_phone=self.telephone,
#             contact_name=self.delivery_contact,
#             notifications=pf_lists.RecipientNotifications.standard_recip(),
#         )
#         try:
#             contact_model = pf_top.Contact(**contact_dict)
#             contact_model.model_validate(contact_model)
#         except _p.ValidationError as err:
#             err_msg = 'missing data, using filler - ' + ', '.join(_['msg'] for _ in err.errors())
#             logger.warning(err_msg)
#             contact_model = pf_top.ContactTemporary(**contact_dict)
#             self.alerts.append(Alert(type=AlertType.WARNING, message=err_msg))
#         return contact_model
#
#     def missing_kit(self) -> list[str] | None:
#         return self.missing_kit_str.splitlines() if self.missing_kit_str else None
#
#
# # def initial_shipment_state(self) -> Shipment:
# #     try:
# #         el_client = ELClient()
# #         chosen = el_client.choose_address(self.input_address())
# #         return Shipment(
# #             contact=self.contact(),
# #             address=chosen,
# #             ship_date=self.send_date,
# #             total_number_of_parcels=self.total_number_of_parcels,
# #             reference_number1=self.customer,
# #         )
# #     except BackendError as err:
# #         logger.exception(
# #             f'Zeep Backend Error prevents retrieving initial state for {self.name}:{str(err)}'
# #         )
# #         raise
#
#
# # class AmherstRecordDB(AmherstRecord, table=True):
# #     id: int | None = sqm.Field(primary_key=True)
# #     booking_states: list['BookingStateDB'] = sqm.Relationship(
# #         back_populates="record",
# #     )
#
#
# def addr_lines_dict_am(address: str) -> dict[str, str]:
#     addr_lines = address.splitlines()
#     if len(addr_lines) < 3:
#         addr_lines.extend([''] * (3 - len(addr_lines)))
#     elif len(addr_lines) > 3:
#         addr_lines[2] = ','.join(addr_lines[2:])
#     return {f'address_line{num}': line for num, line in enumerate(addr_lines, start=1)}
#
#
# def addr_town_lines_maybe(address: str) -> dict[str, str]:
#     addr_lines = address.splitlines()
#     if len(addr_lines) < 3:
#         addr_lines.extend([''] * (3 - len(addr_lines)))
#     elif len(addr_lines) > 3:
#         addr_lines[2] = ','.join(addr_lines[2:])
#     used_lines = [_ for _ in addr_lines if _]
#     town = used_lines.pop() if len(used_lines) > 1 else ''
#     return {
#         f'address_line{num}': line for num, line in enumerate(used_lines, start=1)
#     } | {'town': town}
#
#
# def get_email(fields_enum, record):
#     return (
#             record.get(fields_enum.DELIVERY_EMAIL)
#             or record.get(fields_enum.PRIMARY_EMAIL)
#             or r'EMAIL_NOT_FOUND@FILLMEIN.COM'
#     )
#
#
# @functools.lru_cache
# def get_customer_record(customer: str) -> dict[str, str]:
#     """Get a customer record from `:class:PyCommence`"""
#     logger.debug(f'Getting customer record for {customer}')
#     with PyCommence.from_table_name_context(table_name='Customer') as py_cmc:
#         rec = py_cmc.one_record(customer)
#     # py_cmc = PyCommence.from_table_name(table_name='Customer')
#     # rec = py_cmc.one_record(customer)
#     return rec
#
#
# # class AmherstRecordPartial(AmherstRecord):
# #     delivery_contact: str = Field(
# #         '',
# #         validation_alias=AliasChoices('Delivery Contact', 'Deliv Contact')
# #     )
# #     delivery_business: str = Field(
# #         '',
# #         validation_alias=AliasChoices('Delivery Name', 'Deliv Name', 'Customer', 'To Customer')
# #     )
# #     telephone: str = Field(
# #         '',
# #         validation_alias=AliasChoices('Delivery Tel', 'Deliv Telephone', 'Delivery Telephone')
# #     )
# #     email: str = Field('', validation_alias=AliasChoices('Delivery Email', 'Deliv Email'))
# #     address_str: str = Field(
# #         '',
# #         validation_alias=AliasChoices('Delivery Address', 'Deliv Address')
# #     )
# #     postcode: str = Field('', validation_alias=AliasChoices('Delivery Postcode', 'Deliv Postcode'))
# #
# #     @field_validator('email', mode='after')
# #     def fake_email(cls, v, values):
# #         if not v:
# #             return "THISEMAILNOTREAL@REPLACEME.com"
# #         return v
#
#
# class EmailOption(_p.BaseModel):
#     email: EmailStr
#     description: str
#     name: str
#
#     def __eq__(self, other: 'EmailOption'):
#         return self.email == other.email
