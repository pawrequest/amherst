from __future__ import annotations

from datetime import date, datetime, time
from decimal import Decimal
from pathlib import Path
from typing import Optional

from pydantic import ConfigDict

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


class HireOrder(AmBase):
    special_kit: str
    reprogrammed: bool
    items: HireItems
    radio_type: str


class HireStaff(AmBase):
    packed_by: Optional[str] = None
    unpacked_by: Optional[str] = None
