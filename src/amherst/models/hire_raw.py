from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import ClassVar, Optional

from sqlmodel import Column, Field, JSON

from .shared import (
    HireStatusEnum,
)
from .types import DateMaybe, DecimalAm, ListComma, TimeMaybe
from pycommence.models.cmc_models import CmcModelRaw


class HireRaw(CmcModelRaw, table=True):
    """ Direct representation of Commence Hire Category"""
    cmc_table_name: ClassVar[str] = 'Hire'

    id: Optional[int] = Field(default=None, primary_key=True)
    record: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # hire details
    name: str = Field(alias='Name')
    reference_number: str = Field(alias='Reference Number')
    # customer_name: str = Field(alias='Customer Name')
    customer: str = Field(alias='To Customer', default='')

    # dates and times
    booked_date: DateMaybe = Field(alias='Booked Date')
    send_out_date: DateMaybe = Field(alias='Send Out Date', default_factory=datetime.date)
    due_back_date: DateMaybe = Field(alias='Due Back Date')
    actual_return_date: DateMaybe = Field(alias='Actual Return Date')
    packed_date: DateMaybe = Field(alias='Packed Date')
    packed_time: TimeMaybe = Field(alias='Packed Time')
    unpacked_date: DateMaybe = Field(alias='Unpacked Date')
    unpacked_time: TimeMaybe = Field(alias='Unpacked Time')
    recurring_hire: bool = Field(alias='Recurring Hire')

    # status and notes
    status: HireStatusEnum = Field(alias='Status')
    # status: str = Field(alias='Status')
    closed: bool = Field(alias='Closed')
    sending_status: str = Field(alias='Sending Status')
    return_notes: str = Field(alias='Return Notes')
    db_label_printed: bool = Field(alias='DB label printed')
    pickup_arranged: bool = Field(alias='Pickup Arranged')
    missing_kit: str = Field(alias='Missing Kit')

    # payment
    invoice: Optional[Path] = Field(alias='Invoice', default=None)
    purchase_order: Optional[str] = Field(alias='Purchase Order')
    payment_terms: str = Field(alias='Payment Terms')
    delivery_cost: DecimalAm = Field(alias='Delivery Cost')
    discount_percentage: DecimalAm = Field(alias='Discount Percentage', default=0.0)
    discount_description: str = Field(alias='Discount Description')

    # address
    address: str = Field(alias='Delivery Address')
    contact: str = Field(alias='Delivery Contact')
    email: str = Field(alias='Delivery Email')
    business_name: str = Field(alias='Delivery Name')
    postcode: str = Field(alias='Delivery Postcode')
    telephone: str = Field(alias='Delivery Tel')
    #
    # shipping
    send_collect: str = Field(alias='Send / Collect')
    send_method: str = Field(alias='Send Method')
    boxes: int = Field(alias='Boxes')
    all_address: str = Field(alias='All Address')
    tracking_numbers: ListComma = Field(alias='Tracking Numbers', default_factory=list, sa_column=Column(JSON))

    # staff
    packed_by: str = Field(alias='Packed By')
    unpacked_by: str = Field(alias='Unpacked by')

    # item details
    special_kit: str = Field(alias='Special Kit')
    reprogrammed: bool = Field(alias='Reprogrammed')
    radio_type: str = Field(alias='Radio Type')

    # items
    sgl_charger: int = Field(alias='Number Sgl Charger')
    vhf: int = Field(alias='Number VHF')
    em: int = Field(alias='Number EM')
    vhf_6way: int = Field(alias='Number VHF 6-way')
    icom_psu: int = Field(alias='Number ICOM PSU')
    megaphone: int = Field(alias='Number Megaphone')
    uhf: int = Field(alias='Number UHF')
    uhf_6way: int = Field(alias='Number UHF 6-way')
    parrot: int = Field(alias='Number Parrot')
    headset: int = Field(alias='Number Headset')
    batteries: int = Field(alias='Number Batteries')
    cases: int = Field(alias='Number Cases')
    megaphone_bat: int = Field(alias='Number Megaphone Bat')
    icom: int = Field(alias='Number Icom')
    emc: int = Field(alias='Number EMC')
    headset_big: int = Field(alias='Number Headset Big')
    icom_car_lead: int = Field(alias='Number ICOM Car Lead')
    magmount: int = Field(alias='Number Magmount')
    clipon_aerial: int = Field(alias='Number Clipon Aerial')
    wand: int = Field(alias='Number Wand')
    repeater: int = Field(alias='Number Repeater')
    wand_bat: int = Field(alias='Number Wand Battery')
    wand_charger: int = Field(alias='Number Wand Charger')
    aerial_adapt: int = Field(alias='Number Aerial Adapt')

# class HireCmc(BaseModel):
#     """ Direct representation of Commence Hire Category"""
#
#     class Config:
#         extra = 'ignore'
#
#     name: str = Field(alias='Name')
#     reference_number: str = Field(alias='Reference Number')
#     customer_name: str = Field(alias='Customer Name')
#     to_customer: str = Field(alias='To Customer')
#
#     booked_date: str = Field(alias='Booked Date')
#     send_out_date: str = Field(alias='Send Out Date')
#     due_back_date: str = Field(alias='Due Back Date')
#     actual_return_date: str = Field(alias='Actual Return Date')
#     packed_date: str = Field(alias='Packed Date')
#     packed_time: str = Field(alias='Packed Time')
#     unpacked_date: str = Field(alias='Unpacked Date')
#     unpacked_time: str = Field(alias='Unpacked Time')
#     recurring_hire: bool = Field(alias='Recurring Hire')
#     weeks: int = Field(alias='Weeks')
#
#     status: str = Field(alias='Status')
#     closed: bool = Field(alias='Closed')
#     sending_status: str = Field(alias='Sending Status')
#     return_notes: str = Field(alias='Return Notes')
#     db_label_printed: bool = Field(alias='DB label printed')
#     pickup_arranged: bool = Field(alias='Pickup Arranged')
#     missing_kit: str = Field(alias='Missing Kit')
#
#     invoice: FilePath = Field(alias='Invoice')
#     purchase_order: Path = Field(alias='Purchase Order')
#     payment_terms: str = Field(alias='Payment Terms')
#     delivery_cost: Decimal = Field(alias='Delivery Cost')
#     discount_percentage: Decimal = Field(alias='Discount Percentage')
#     discount_description: str = Field(alias='Discount Description')
#
#     special_kit: str = Field(alias='Special Kit')
#     reprogrammed: bool = Field(alias='Reprogrammed')
#     radio_type: str = Field(alias='Radio Type')
#
#     send_collect: str = Field(alias='Send / Collect')
#     send_method: str = Field(alias='Send Method')
#     boxes: int = Field(alias='Boxes')
#     all_address: str = Field(alias='All Address')
#     tracking_numbers: list = Field(alias='Tracking Numbers')
#
#     packed_by: str = Field(alias='Packed By')
#     unpacked_by: str = Field(alias='Unpacked by')


# import re
# from datetime import date, datetime, time
# from decimal import Decimal
# from pathlib import Path
# from typing import Optional
#
# from pydantic import BaseModel, Field, FilePath, model_validator
#
#
# class HireDates(BaseModel):
#     booked: date
#     send_out: date
#     due_back: date
#     weeks: int
#     actual_return: date = None
#     packed_date: date
#     packed_time: time
#     unpacked_date: date
#     unpacked_time: time
#     recurring_hire: bool
#
#     @property
#     def unpacked_dt(self):
#         return datetime.combine(self.unpacked_date, self.unpacked_time)
#
#     @property
#     def packed_dt(self):
#         return datetime.combine(self.packed_date, self.packed_time)
#
#     @model_validator(mode='before')
#     def dates(cls, values):
#         for k, v in values.items():
#             if re.match(r'(\d{2})/(\d{2})/(\d{4})', v):
#                 values[k] = datetime.strptime(v, '%d/%m/%Y').date()
#             elif re.match(r'(\d{2}):(\d{2})', v):
#                 values[k] = datetime.strptime(v, '%H:%M').time()
#         return values
#
#     @model_validator(mode='before')
#     def times(cls, values):
#         for k, v in values.items():
#             if re.match(r'(\d{2}):(\d{2})', v):
#                 values[k] = datetime.strptime(v, '%H:%M').time()
#         return values
#
#
# class HireStatus(BaseModel):
#     status: str
#     closed: bool
#     return_notes: str
#     sending_status: str
#     pickup_arranged: bool
#     db_label_printed: bool
#     missing_kit: str
#
#
# class HireShipping(BaseModel):
#     delivery_cost: Decimal
#     send_collect: str
#     send_method: str
#     all_address: str
#     tracking_numbers: list
#     boxes: int
#     tracking_numbers: list
#
#
# class HirePayment(BaseModel):
#     invoice: FilePath
#     purchase_order: Optional[FilePath]
#     payment_terms: str
#     discount_percentage: Decimal
#     discount_description: str
#
#
# class HireItems(BaseModel):
#     class Config:
#         extra = 'ignore'
#
#     sgl_charger: int = Field(alias='Number Sgl Charger')
#     vhf: int = Field(alias='Number VHF')
#     em: int = Field(alias='Number EM')
#     vhf_6way: int = Field(alias='Number VHF 6-way')
#     icom_psu: int = Field(alias='Number ICOM PSU')
#     megaphone: int = Field(alias='Number Megaphone')
#     uhf: int = Field(alias='Number UHF')
#     uhf_6way: int = Field(alias='Number UHF 6-way')
#     parrot: int = Field(alias='Number Parrot')
#     headset: int = Field(alias='Number Headset')
#     batteries: int = Field(alias='Number Batteries')
#     cases: int = Field(alias='Number Cases')
#     megaphone_bat: int = Field(alias='Number Megaphone Bat')
#     icom: int = Field(alias='Number Icom')
#     emc: int = Field(alias='Number EMC')
#     headset_big: int = Field(alias='Number Headset Big')
#     icom_car_lead: int = Field(alias='Number ICOM Car Lead')
#     magmount: int = Field(alias='Number Magmount')
#     clipon_aerial: int = Field(alias='Number Clipon Aerial')
#     wand: int = Field(alias='Number Wand')
#     repeater: int = Field(alias='Number Repeater')
#     wand_bat: int = Field(alias='Number Wand Battery')
#     wand_charger: int = Field(alias='Number Wand Charger')
#     aerial_adapt: int = Field(alias='Number Aerial Adapt')
#
#
# class HireOrder(BaseModel):
#     special_kit: str
#     reprogrammed: bool
#     items: HireItems
#     radio_type: str
#
#
# class HireStaff(BaseModel):
#     packed_by: str
#     unpacked_by: str
#
#
# class HireCmc(BaseModel):
#     # config to ignore extras
#     class Config:
#         extra = 'ignore'
#
#     name: str = Field(alias='Name')
#     reference_number: str = Field(alias='Reference Number')
#     customer_name: str = Field(alias='Customer Name')
#     to_customer: str = Field(alias='To Customer')
#
#
#     booked_date: str = Field(alias='Booked Date')
#     send_out_date: str = Field(alias='Send Out Date')
#     due_back_date: str = Field(alias='Due Back Date')
#     actual_return_date: str = Field(alias='Actual Return Date')
#     packed_date: str = Field(alias='Packed Date')
#     packed_time: str = Field(alias='Packed Time')
#     unpacked_date: str = Field(alias='Unpacked Date')
#     unpacked_time: str = Field(alias='Unpacked Time')
#     recurring_hire: bool = Field(alias='Recurring Hire')
#     weeks: int = Field(alias='Weeks')
#
#
#     status: str = Field(alias='Status')
#     closed: bool = Field(alias='Closed')
#     sending_status: str = Field(alias='Sending Status')
#     return_notes: str = Field(alias='Return Notes')
#     db_label_printed: bool = Field(alias='DB label printed')
#     pickup_arranged: bool = Field(alias='Pickup Arranged')
#     missing_kit: str = Field(alias='Missing Kit')
#
#
#     invoice: FilePath = Field(alias='Invoice')
#     purchase_order: Path = Field(alias='Purchase Order')
#     payment_terms: str = Field(alias='Payment Terms')
#     delivery_cost: Decimal = Field(alias='Delivery Cost')
#     discount_percentage: Decimal = Field(alias='Discount Percentage')
#     discount_description: str = Field(alias='Discount Description')
#
#
#     special_kit: str = Field(alias='Special Kit')
#     reprogrammed: bool = Field(alias='Reprogrammed')
#     radio_type: str = Field(alias='Radio Type')
#
#
#
#     send_collect: str = Field(alias='Send / Collect')
#     send_method: str = Field(alias='Send Method')
#     boxes: int = Field(alias='Boxes')
#     all_address: str = Field(alias='All Address')
#     tracking_numbers: list = Field(alias='Tracking Numbers')
#
#
#     packed_by: str = Field(alias='Packed By')
#     unpacked_by: str = Field(alias='Unpacked by')
#
#
# class HireNew(BaseModel):
#     hire_name: str
#     to_customer: str
#     hire_dates: HireDates
#     hire_status: HireStatus
#     hire_shipping: HireShipping
#     hire_payment: HirePayment
#     hire_items: HireItems
#     hire_staff: HireStaff
#
#     @classmethod
#     def from_hire_cmc(cls, hire: HireCmc):
#         return cls(
#             hire_name=hire.name,
#             to_customer=hire.to_customer,
#             hire_dates=HireDates(
#                 booked=hire.booked_date,
#                 send_out=hire.send_out_date,
#                 due_back=hire.due_back_date,
#                 weeks=hire.weeks,
#                 actual_return=None,
#                 packed_date=hire.packed_date,
#                 packed_time=hire.packed_time,
#                 unpacked_date=hire.unpacked_date,
#                 unpacked_time=hire.unpacked_time,
#                 recurring_hire=hire.recurring_hire
#             ),
#             hire_status=HireStatus(
#                 status=hire.status,
#                 closed=hire.closed,
#                 return_notes=hire.return_notes,
#                 sending_status=hire.sending_status,
#                 pickup_arranged=hire.pickup_arranged,
#                 db_label_printed=hire.db_label_printed,
#                 missing_kit=hire.missing_kit
#             ),
#             hire_shipping=HireShipping(
#                 delivery_cost=hire.delivery_cost,
#                 send_collect=hire.send_collect,
#                 send_method=hire.send_method,
#                 all_address=hire.all_address,
#                 tracking_numbers=hire.tracking_numbers,
#                 boxes=hire.boxes
#             ),
#             hire_payment=HirePayment(
#                 invoice=hire.invoice,
#                 purchase_order=hire.purchase_order,
#                 payment_terms=hire.payment_terms,
#                 discount_description=hire.discount_description,
#                 discount_percentage=hire.discount_percentage
#             ),
#             hire_items=HireItems(**hire.model_dump()),
#             hire_staff=HireStaff(
#                 packed_by=hire.packed_by,
#                 unpacked_by=hire.unpacked_by
#             )
#         )
#
