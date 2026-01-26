import secrets
import string
from datetime import date
from enum import StrEnum, auto

from dateutil.utils import today
from pydantic import BaseModel, Field, model_validator


def generate_rma_number(customer_name: str) -> str:
    abbrev = customer_name[:8].upper()
    today_str = date.today().strftime("%Y%m%d")
    rand_suffix = ''.join(secrets.choice(string.digits) for _ in range(4))
    return f"{abbrev}-{today_str}-{rand_suffix}"


class ItemCategory(StrEnum):
    radio = auto()
    battery = auto()
    antenna = auto()
    charger = auto()


class ReturnItem(BaseModel):
    category: ItemCategory
    reason: str
    identifying_marks: str | None = None
    serial_number: str | None = None


class RMA(BaseModel):
    customer_name: str
    date_booked: date = Field(default_factory=today)
    date_recieved: date | None = None
    date_returned: date | None = None
    rma_number: str | None = None  # auto generated
    technician: str | None = None
    notes: str | None = None
    items_returned: list[ReturnItem] = Field(default_factory=list[ReturnItem])

    @model_validator(mode='after')
    def set_rma_number(self):
        if self.rma_number is None:
            self.rma_number = generate_rma_number(self.customer_name)
        return self
