from __future__ import annotations

from abc import ABC
from datetime import date, time
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

from pydantic import ConfigDict, field_validator
from sqlmodel import Column, Field, JSON, SQLModel

from amherst.models.shared import HireStatusEnum
from shipr.express import types as elt
from shipr.express.enums import ServiceCode


class AmBaseDB(SQLModel, ABC):
    model_config = ConfigDict(
        use_enum_values=True,
    )


class ContactAm(AmBaseDB):
    email: str
    name: str
    telephone: str


class HireShipping(AmBaseDB):
    send_collect: str = Field(default="")
    send_method: str = Field(default="")
    all_address: str = Field(default="")
    tracking_numbers: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    boxes: int = Field(default=0)


class HireDates(AmBaseDB):
    booked_date: Optional[date] = Field(default=None)
    send_out_date: Optional[date] = Field(default_factory=date.today)
    due_back_date: Optional[date] = Field(default=None)
    actual_return_date: Optional[date] = Field(default=None)
    packed_date: Optional[date] = Field(default=None)
    unpacked_date: Optional[date] = Field(default=None)
    packed_time: Optional[time] = Field(default=None)
    unpacked_time: Optional[time] = Field(default=None)
    recurring_hire: bool = Field(default=False)


class HireStatus(AmBaseDB):
    status: HireStatusEnum
    closed: bool = Field(default=False)
    return_notes: str = Field(default="")
    sending_status: str = Field(default="")
    pickup_arranged: bool = Field(default=False)
    db_label_printed: bool = Field(default=False)
    missing_kit: str = Field(default="")


class HirePayment(AmBaseDB):
    invoice: Optional[Path] = Field(default=None)
    purchase_order: Optional[str] = Field(default=None)
    payment_terms: str = Field(default="")
    discount_percentage: Decimal = Field(default=Decimal(0))
    discount_description: str = Field(default="")
    delivery_cost: Decimal = Field(default=Decimal(0))


class HireItems(AmBaseDB):
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


class HireOrder(AmBaseDB):
    hire_items: Optional[HireItems] = Field(default=None, sa_column=Column(JSON))
    special_kit: str = Field(default="")
    reprogrammed: bool = Field(default=False)
    radio_type: str = Field(default="")


class HireStaff(AmBaseDB):
    packed_by: Optional[str] = Field(default=None)
    unpacked_by: Optional[str] = Field(default=None)


class HireState(AmBaseDB):
    boxes: int = 1
    ship_date: Optional[date] = Field(default_factory=date.today)
    ship_service: Optional[ServiceCode] = ServiceCode.EXPRESS24
    candidates: list[elt.AddressPF] = Field(default_factory=list, sa_column=Column(JSON))
    recipient_address: Optional[elt.AddressPF] = Field(default=None, sa_column=Column(JSON))
    recipient_contact: Optional[elt.ContactPF] = Field(default=None, sa_column=Column(JSON))

    @field_validator('ship_date', mode='after')
    def validate_ship_date(cls, v):
        tod = date.today()
        return v if v >= tod else tod
