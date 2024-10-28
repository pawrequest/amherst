# # from __future__ import annotations
# from datetime import date
#
# import pydantic as _p
# import sqlmodel as sqm
# from loguru import logger
# from pawdantic.pawsql import default_json_field
# from pydantic import AliasChoices, ConfigDict, Field
#
# from amherst.commence_adaptors import CustomerAliases, AM_SHIP_DATE, AmherstTableName, EmailOption
# from amherst.importer import split_addr_str
# from pycommence.pycommence_v1 import PyCommence
# from shipaw.models import pf_lists, pf_models, pf_top
# from shipaw.models.pf_models import AddressChoice
# from shipaw.models.pf_msg import Alert, Alerts
# from shipaw.ship_types import AlertType
#
#
# class AmherstRecordIn(sqm.SQLModel):
#     model_config = ConfigDict(
#         populate_by_name=True,
#         validate_default=True,
#     )
#     category: AmherstTableName
#     alerts: Alerts = default_json_field(Alerts, Alerts.empty)
#     # alerts: list[Alert] | None = optional_json_field(Alert)
#     name: str = Field(..., alias='Name')
#     customer: str = Field(..., validation_alias=AliasChoices('To Customer', 'Name'))
#     send_date: AM_SHIP_DATE
#     delivery_contact: str = Field(..., validation_alias=AliasChoices('Delivery Contact', 'Deliv Contact'))
#     delivery_business: str = Field(
#         ..., validation_alias=AliasChoices('Delivery Name', 'Deliv Name', 'Customer', 'To Customer')
#     )
#     telephone: str = Field(..., validation_alias=AliasChoices('Delivery Tel', 'Deliv Telephone', 'Delivery Telephone'))
#     email: str = Field('', validation_alias=AliasChoices('Delivery Email', 'Deliv Email'))
#     address_str: str = Field(..., validation_alias=AliasChoices('Delivery Address', 'Deliv Address'))
#
#     postcode: str = Field(..., validation_alias=AliasChoices('Delivery Postcode', 'Deliv Postcode'))
#     send_method: str = Field('', validation_alias=AliasChoices('Send Method', 'Delivery Method'))
#     invoice_path: str | None = Field(None, validation_alias=AliasChoices('Invoice', 'Invoice Path'))
#     missing_kit_str: str | None = Field(None, alias='Missing Kit')
#     boxes: int = Field(1, alias='Boxes')
#     track_in: str | None = Field(None, alias='Track Inbound')
#     track_out: str | None = Field(None, alias='Track Outbound')
#     address_choice: AddressChoice | None = None
#
#     @property
#     def email_options(self):
#         cust = self.customer_record()
#         email_dict = {
#             cust.get(CustomerAliases.ACCOUNTS_EMAIL): ('accounts', 'Customer Accounts'),
#             cust.get(CustomerAliases.PRIMARY_EMAIL): ('primary', 'Customer Primary'),
#             cust.get(CustomerAliases.DELIVERY_EMAIL): ('cust_del', 'Customer Default Delivery'),
#             cust.get(CustomerAliases.INVOICE_EMAIL): ('invoice', 'Customer Invoice'),
#             self.email: ('rec_del', f'{self.category.title()} Delivery'),
#         }
#         options = [
#             EmailOption(name=name, email=email, description=description)
#             for email, (name, description) in email_dict.items()
#             if email
#         ]
#         return options
#
#     def customer_record(self) -> dict[str, str]:
#         return self.model_dump() if self.category == 'Customer' else get_customer_record(self.customer)
#
#     @property
#     def input_address(self):
#         return pf_models.AddressRecipient(
#             **split_addr_str(self.address_str),
#             postcode=self.postcode,
#         )
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
#             errors = err.errors()
#             reasons = [_.get('ctx').get('reason') for _ in errors]
#             err_msg = ', '.join(reasons)
#             logger.warning(err_msg)
#             contact_model = pf_top.ContactTemporary(**contact_dict)
#             self.alerts.alert.append(Alert(type=AlertType.ERROR, message=err_msg))
#         return contact_model
#
#     def missing_kit(self) -> list[str] | None:
#         return self.missing_kit_str.splitlines() if self.missing_kit_str else None
#
#
# class AmherstRecord(AmherstRecordIn):
#     send_date: date
#
#
# # class AmherstRecordDB(AmherstRecord, table=True):
# #     id: int | None = sqlmodel.Field(default=None, primary_key=True)
# #     address_choice: AddressChoice | None = optional_json_field(AddressChoice)
#
#
# def get_customer_record(customer: str) -> dict[str, str]:
#     """Get a customer record from `:class:PyCommence`"""
#     logger.debug(f'Getting customer record for {customer}')
#     with PyCommence.with_csr(csrname='Customer') as py_cmc:
#         rec = py_cmc.one_record(customer)
#     return rec
