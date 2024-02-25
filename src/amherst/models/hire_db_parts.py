from abc import ABC
from datetime import date, time
from decimal import Decimal
from pathlib import Path
from typing import List, Optional

from pydantic import ConfigDict, BaseModel
from sqlmodel import Column, Field, JSON, Relationship, SQLModel

from amherst.models.shared import HireStatusEnum


class AmBaseDB(SQLModel, ABC):
    model_config = ConfigDict(
        use_enum_values=True,
    )


class ContactAm(AmBaseDB, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hire_id: Optional[int] = Field(default=None, foreign_key="hire.id")
    email: str
    name: str
    telephone: str


class AddressAm(AmBaseDB, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hire_id: Optional[int] = Field(default=None, foreign_key="hire.id")

    address: str
    contact: str
    email: str
    postcode: str
    telephone: str

    @property
    def addr_lines(self) -> list[str]:
        addr_lines = self.address.splitlines()
        if len(addr_lines) < 3:
            addr_lines.extend([''] * (3 - len(addr_lines)))
        elif len(addr_lines) > 3:
            addr_lines[2] = ','.join(addr_lines[2:])
        return addr_lines


    @property
    def addr_lines_dict(self) -> dict[str, str]:
        addr_lines = self.address.splitlines()
        if len(addr_lines) < 3:
            addr_lines.extend([''] * (3 - len(addr_lines)))
        elif len(addr_lines) > 3:
            addr_lines[2] = ','.join(addr_lines[2:])
        return {
            f'address_line{num}': line
            for num, line in enumerate(addr_lines, start=1)
        }


class HireShipping(AmBaseDB, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hire_id: Optional[int] = Field(default=None, foreign_key="hire.id", unique=True)

    send_collect: str = Field(default="")
    send_method: str = Field(default="")
    all_address: str = Field(default="")
    tracking_numbers: List[str] = Field(default_factory=list, sa_column=Column(JSON))
    boxes: int = Field(default=0)


class HireDates(AmBaseDB, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hire_id: Optional[int] = Field(default=None, foreign_key="hire.id")

    booked_date: Optional[date] = Field(default=None)
    send_out_date: Optional[date] = Field(default_factory=date.today)
    due_back_date: Optional[date] = Field(default=None)
    actual_return_date: Optional[date] = Field(default=None)
    packed_date: Optional[date] = Field(default=None)
    unpacked_date: Optional[date] = Field(default=None)
    packed_time: Optional[time] = Field(default=None)
    unpacked_time: Optional[time] = Field(default=None)
    recurring_hire: bool = Field(default=False)


class HireStatus(AmBaseDB, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hire_id: Optional[int] = Field(default=None, foreign_key="hire.id")

    status: HireStatusEnum
    closed: bool = Field(default=False)
    return_notes: str = Field(default="")
    sending_status: str = Field(default="")
    pickup_arranged: bool = Field(default=False)
    db_label_printed: bool = Field(default=False)
    missing_kit: str = Field(default="")


class HirePayment(AmBaseDB, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hire_id: Optional[int] = Field(default=None, foreign_key="hire.id")

    invoice: Optional[Path] = Field(default=None)
    purchase_order: Optional[str] = Field(default=None)
    payment_terms: str = Field(default="")
    discount_percentage: Decimal = Field(default=Decimal(0))
    discount_description: str = Field(default="")
    delivery_cost: Decimal = Field(default=Decimal(0))


class HireItems(AmBaseDB, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: Optional[int] = Field(default=None, foreign_key="hireorder.id")
    # order: Optional['HireOrder'] = Relationship(back_populates="items")

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
    # Include all your fields here as in your original model


class HireOrder(AmBaseDB, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hire_id: Optional[int] = Field(default=None, foreign_key="hire.id")
    items_id: Optional[int] = Field(default=None, foreign_key="hireitems.id")
    items: Optional[HireItems] = Relationship(
                sa_relationship_kwargs={
                    "primaryjoin": "HireItems.order_id==HireOrder.id",
                    "lazy": "joined",
                },
            )

    special_kit: str = Field(default="")
    reprogrammed: bool = Field(default=False)
    radio_type: str = Field(default="")


class HireStaff(AmBaseDB, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hire_id: Optional[int] = Field(default=None, foreign_key="hire.id")
    packed_by: Optional[str] = Field(default=None)
    unpacked_by: Optional[str] = Field(default=None)
