from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field
from sqlmodel import SQLModel

from pycommence.filters import CmcFilter, FilterCondition
from .shared import (AmAddress, HireStatusEnum)
from pycommence.models.cmc_models import CmcModel, sub_model_from_cmc
from .hire_cmc import HireCmc

INITIAL_FILTER_ARRAY = [
    CmcFilter(
        field_name='Status',
        condition=FilterCondition.EQUAL_TO,
        value=HireStatusEnum.BOOKED_IN,
    )
]


def get_array():
    return INITIAL_FILTER_ARRAY


class HireDates(BaseModel):
    booked_date: Optional[date]
    send_out_date: Optional[date] = Field(default_factory=date.today)
    due_back_date: Optional[date]
    actual_return_date: Optional[date]
    packed_date: Optional[date]
    unpacked_date: Optional[date]

    packed_time: Optional[time]
    unpacked_time: Optional[time]

    # weeks: int
    recurring_hire: bool

    @property
    def unpacked_dt(self):
        return datetime.combine(self.unpacked_date, self.unpacked_time)

    @property
    def packed_dt(self):
        return datetime.combine(self.packed_date, self.packed_time)


class HireStatus(BaseModel):
    status: HireStatusEnum
    closed: bool
    return_notes: str
    sending_status: str
    pickup_arranged: bool
    db_label_printed: bool
    missing_kit: str


class HireShipping(BaseModel):
    send_collect: str
    send_method: str
    all_address: str
    tracking_numbers: list
    boxes: int


class HirePayment(BaseModel):
    invoice: Path
    purchase_order: Optional[str]
    payment_terms: str
    discount_percentage: Decimal
    discount_description: str
    delivery_cost: Decimal


class HireItems(BaseModel):
    sgl_charger: int
    vhf: int
    em: int
    vhf_6way: int
    icom_psu: int
    megaphone: int
    uhf: int
    uhf_6way: int
    parrot: int
    headset: int
    batteries: int
    cases: int
    megaphone_bat: int
    icom: int
    emc: int
    headset_big: int
    icom_car_lead: int
    magmount: int
    clipon_aerial: int
    wand: int
    repeater: int
    wand_bat: int
    wand_charger: int
    aerial_adapt: int


class HireOrder(BaseModel):
    special_kit: str
    reprogrammed: bool
    items: HireItems
    radio_type: str


class HireStaff(BaseModel):
    packed_by: Optional[str] = None
    unpacked_by: Optional[str] = None


# class Hire(CmcModel):
class Hire(CmcModel, SQLModel, table=True):
    """ Primary Hire Type """
    cmc_class = HireCmc

    class Config:
        arbitrary_types_allowed = True

    name: str
    customer: str
    dates: HireDates
    status: HireStatus
    shipping: HireShipping
    delivery_address: AmAddress
    payment: HirePayment
    items: HireItems
    staff: HireStaff

    # initial_filter_array: ClassVar[list[CmcFilterPy]] = INITIAL_FILTER_ARRAY

    @classmethod
    def from_cmc(cls, cmc_obj: HireCmc) -> Hire:
        return cls.model_validate(
            dict(
                name=cmc_obj.name,
                customer=cmc_obj.customer,
                dates=sub_model_from_cmc(HireDates, cmc_obj),
                status=sub_model_from_cmc(HireStatus, cmc_obj),
                shipping=sub_model_from_cmc(HireShipping, cmc_obj),
                delivery_address=sub_model_from_cmc(AmAddress, cmc_obj, prepend='delivery_'),
                payment=sub_model_from_cmc(HirePayment, cmc_obj),
                items=sub_model_from_cmc(HireItems, cmc_obj),
                staff=sub_model_from_cmc(HireStaff, cmc_obj),
            )
        )

    @classmethod
    def rout_prefix(cls) -> str:
        return '/hires/'

    # @classmethod
    # def from_name(cls, name: str) -> Hire:
    #     db = CmcDB()
    #     cursor = db.get_cursor(cls.converted_class.table_name)
    #     record = cursor.get_record(name)
    #     cmc = cls.converted_class(**record)
    #     return cls.from_cmc(cmc)
