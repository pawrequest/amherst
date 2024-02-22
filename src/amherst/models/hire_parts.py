from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Optional

from pydantic import ConfigDict, model_validator, field_validator

from amherst.models.shared import HireStatusEnum
from pydantic import BaseModel, Field


class AmBase(BaseModel):
    model_config = ConfigDict(
    )
    pass


class HireDates(AmBase):
    # booked_date: Optional[datetime] = Field(default=None)
    # send_out_date: Optional[datetime] = Field(default_factory=date.today)
    # due_back_date: Optional[datetime] = Field(default=None)
    # actual_return_date: Optional[datetime] = Field(default=None)
    # packed_date: Optional[datetime] = Field(default=None)
    # unpacked_date: Optional[datetime] = Field(default=None)
    #
    # packed_time: Optional[datetime] = Field(default=None)
    # unpacked_time: Optional[datetime] = Field(default=None)
    #
    booked_date: Optional[date] = Field(default=None)
    send_out_date: Optional[date] = Field(default_factory=date.today)
    due_back_date: Optional[date] = Field(default=None)
    actual_return_date: Optional[date] = Field(default=None)
    packed_date: Optional[date] = Field(default=None)
    unpacked_date: Optional[date] = Field(default=None)

    packed_time: Optional[time] = Field(default=None)
    unpacked_time: Optional[time] = Field(default=None)

    # weeks: int
    recurring_hire: bool = Field(default=False)

    @field_validator('send_out_date')
    def overdue(cls, v):
        if v and v < date.today():
            v = date.today()
        return v

    @property
    def unpacked_dt(self):
        if all([self.unpacked_date, self.unpacked_time]):
            return datetime.combine(self.unpacked_date, self.unpacked_time)
        return None

    @property
    def packed_dt(self):
        if all([self.packed_date, self.packed_time]):
            return datetime.combine(self.packed_date, self.packed_time)
        return None


class HireStatus(AmBase):
    model_config = ConfigDict(
        # use_enum_values=True,
    )

    status: HireStatusEnum
    closed: bool
    return_notes: str
    sending_status: str
    pickup_arranged: bool
    db_label_printed: bool
    missing_kit: str


class HireShipping(AmBase):
    send_collect: str
    send_method: str
    all_address: str
    tracking_numbers: list
    boxes: int


class HirePayment(AmBase):
    invoice: Path
    purchase_order: Optional[str]
    payment_terms: str
    discount_percentage: Decimal
    discount_description: str
    delivery_cost: Decimal


class HireItems(AmBase):
    sgl_charger: Optional[int] = Field(0)
    vhf: Optional[int] = Field(0)
    em: Optional[int] = Field(0)
    vhf_6way: Optional[int] = Field(0)
    icom_psu: Optional[int] = Field(0)
    megaphone: Optional[int] = Field(0)
    uhf: Optional[int] = Field(0)
    uhf_6way: Optional[int] = Field(0)
    parrot: Optional[int] = Field(0)
    headset: Optional[int] = Field(0)
    batteries: Optional[int] = Field(0)
    cases: Optional[int] = Field(0)
    megaphone_bat: Optional[int] = Field(0)
    icom: Optional[int] = Field(0)
    emc: Optional[int] = Field(0)
    headset_big: Optional[int] = Field(0)
    icom_car_lead: Optional[int] = Field(0)
    magmount: Optional[int] = Field(0)
    clipon_aerial: Optional[int] = Field(0)
    wand: Optional[int] = Field(0)
    repeater: Optional[int] = Field(0)
    wand_bat: Optional[int] = Field(0)
    wand_charger: Optional[int] = Field(0)
    aerial_adapt: Optional[int] = Field(0)

    @model_validator(mode='before')
    def nones(cls, vls):
        return {k: v for k, v in vls.items() if v}



class HireOrder(AmBase):
    special_kit: str
    reprogrammed: bool
    items: HireItems
    radio_type: str


class HireStaff(AmBase):
    packed_by: Optional[str] = None
    unpacked_by: Optional[str] = None
