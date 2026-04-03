# from __future__ import annotations
#
# from abc import ABC
# from datetime import date
# from typing import ClassVar
#
# from pycommence.pycmc_types import RowInfo
# from pydantic import Field, field_validator
# from shipaw.models.address import Address as AddressAgnost
# from shipaw.models.address import Contact, FullContact
# from shipaw.utils.consts_enums import ShipDirection
#
# from amherst.models.amherst_base import AmherstBase, alias_lookup
# from amherst.models.commence_adaptors import (
#     CategoryName,
#     CommenceDate,
#     CommencePath,
#     CommenceString,
#     CSVSpaces,
#     HireStatus,
#     SaleStatus,
#     split_addr_str2,
# )
# from amherst.models.meta import register_table
# from amherst.models.shipment import AmherstShipment
#
#
# class AmherstShipableBase(AmherstBase, ABC):
#     row_info: RowInfo  # commence row info
#     # amherst common fieldnames fields
#     name: CommenceString = Field(..., alias='Name')
#     shipped_shipments: CSVSpaces = Field('', alias='Shipped Shipment')
#
#     # mandatory fields
#     customer_name: CommenceString
#     delivery_contact_name: CommenceString
#     delivery_contact_business: CommenceString
#     delivery_contact_phone: CommenceString
#     delivery_contact_email: CommenceString
#     delivery_address_str: CommenceString
#     delivery_address_pc: CommenceString
#
#     # optional fields with default
#     send_date: CommenceDate = Field(default_factory=date.today)
#     booking_date: CommenceDate | None = Field(None, alias='Booked Date')
#
#     boxes: int = Field(default=1, alias='Boxes')
#
#     delivery_method: CommenceString | None = None
#
#     @field_validator('send_date', mode='after')
#     def validate_send_date(cls, v: CommenceDate) -> date:
#         if v is None or v < date.today():
#             return date.today()
#         return v
#
#     @property
#     def full_contact(self) -> FullContact:
#         addrlines, town = split_addr_str2(self.delivery_address_str)
#         return FullContact(
#             contact=Contact(
#                 contact_name=self.delivery_contact_name,
#                 mobile_phone=self.delivery_contact_phone,
#                 email_address=self.delivery_contact_email,
#             ),
#             address=AddressAgnost(
#                 address_lines=addrlines,
#                 town=town,
#                 postcode=self.delivery_address_pc,
#                 business_name=self.delivery_contact_business,
#             ),
#         )
#
#     def shipment(self, direction: ShipDirection = ShipDirection.OUTBOUND) -> AmherstShipment:
#         return AmherstShipment(
#             recipient=self.full_contact,
#             boxes=self.boxes,
#             shipping_date=self.send_date,
#             direction=direction,
#             reference=self.customer_name,
#             context={'record': self},
#         )
#
#
# @register_table
# class AmherstCustomer(AmherstShipableBase):
#     category: ClassVar[CategoryName] = CategoryName.Customer
#     customer_name: CommenceString = Field(alias='Name')
#
#     delivery_contact_name: CommenceString = Field(alias='Deliv Contact')
#     delivery_contact_business: CommenceString = Field(alias='Deliv Name')
#     delivery_contact_phone: CommenceString = Field(alias='Deliv Telephone')
#     delivery_contact_email: CommenceString = Field(alias='Deliv Email')
#     delivery_address_str: CommenceString = Field(alias='Deliv Address')
#     delivery_address_pc: CommenceString = Field(alias='Deliv Postcode')
#
#     # customer fields
#     invoice_email: CommenceString = Field('', alias='Invoice Email')
#     accounts_email: CommenceString = Field('', alias='Accounts Email')
#     invoice_address_str: CommenceString = Field('', alias='Invoice Address')
#     invoice_contact: CommenceString = Field('', alias='Invoice Contact')
#     invoice_name: CommenceString = Field('', alias='Invoice Name')
#     invoice_postcode: CommenceString = Field('', alias='Invoice Postcode')
#     invoice_telephone: CommenceString = Field('', alias='Invoice Telephone')
#     primary_email: CommenceString = Field('', alias='Primary Email')
#     date_last_contacted: CommenceDate | None = Field(None, alias='Date Last Contact')
#
#     hires: CSVSpaces = Field('', alias='Has Hired Hires')
#     sales: CSVSpaces = Field('', alias='Involves Sale')
#
#
# class AmherstOrderBase(AmherstShipableBase, ABC):
#     status: CommenceString | None = Field(None, alias='Status')
#     invoice: CommencePath | None = Field(None, alias='Invoice')
#     customer_name: CommenceString = Field(alias='To Customer')
#     order_date: CommenceDate | None = Field(None, alias='Order Date')
#     delivery_method: CommenceString = Field('', alias='Delivery Method')
#
#     delivery_contact_business: CommenceString = Field(alias='Delivery Name')
#     delivery_contact_name: CommenceString = Field(alias='Delivery Contact')
#     delivery_contact_email: CommenceString = Field(alias='Delivery Email')
#     delivery_contact_phone: CommenceString = Field(alias='Delivery Telephone')
#
#     delivery_address_str: CommenceString = Field(alias='Delivery Address')
#     delivery_address_pc: CommenceString = Field(alias='Delivery Postcode')
#
#
# @register_table
# class AmherstHire(AmherstOrderBase):
#     category: ClassVar[CategoryName] = CategoryName.Hire
#
#     delivery_contact_phone: CommenceString = Field(alias='Delivery Tel')
#     delivery_method: CommenceString = Field('', alias='Send Method')
#
#     send_date: CommenceDate = Field(default_factory=date.today, alias='Send Out Date')
#
#     # order overides
#     status: HireStatus = Field(alias='Status')
#
#     # hire fields
#     missing_kit_str: CommenceString | None = Field(None, alias='Missing Kit')
#     due_back_date: CommenceDate = Field(None, alias='Due Back Date')
#     return_notes: CommenceString | None = Field(None, alias='Return Notes')
#     number_uhf: int = Field(0, alias='Number UHF')
#     radio_type: CommenceString | None = Field(None, alias='Radio Type')
#     number_parrot: int = Field(0, alias='Number Parrot')
#     arranged_in: bool = Field(False, alias='Pickup Arranged')
#     arranged_out: bool = Field(False, alias='DB label printed')
#     pickup_date: CommenceDate | None = Field(None, alias='Pickup Date')
#
#
# @register_table
# class AmherstSale(AmherstOrderBase):
#     category: ClassVar[CategoryName] = CategoryName.Sale
#
#     delivery_method: CommenceString | None = None
#
#     # optional overrides order
#     status: SaleStatus = Field(None, alias='Status')
#     booking_date: CommenceDate | None = Field(None, alias='Date Ordered')
#
#     # sale fields
#     lost_equipment: CommenceString | None = Field(None, alias='Lost Equipment')
#     purchase_order: CommenceString | None = Field(None, alias='Purchase Order')
#
#
# @register_table
# class AmherstTrial(AmherstOrderBase):
#     category: ClassVar[CategoryName] = CategoryName.Trial
#
#
# AMHERST_ORDER_MODELS = AmherstHire | AmherstSale
# SALE_BOOKED_DATE_ALIAS = alias_lookup(AmherstSale, 'booking_date')
# HIRE_SEND_DATE_ALIAS = alias_lookup(AmherstHire, 'send_date')
# HIRE_STATUS_ALIAS = alias_lookup(AmherstHire, 'status')
# HIRE_ALIAS_UHF = alias_lookup(AmherstHire, 'number_uhf')
# HIRE_ALIAS_DUE_BACK = alias_lookup(AmherstHire, 'due_back_date')
# HIRE_ALIAS_RADIO_TYPE = alias_lookup(AmherstHire, 'radio_type')
# HIRE_ALIAS_PARROT = alias_lookup(AmherstHire, 'number_parrot')
