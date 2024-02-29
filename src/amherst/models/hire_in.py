from datetime import date
from typing import ClassVar, Optional, Sequence

from pydantic import field_validator
import sqlmodel as sqm

from shipr.models.booking_state import BookingStateIn
from amherst.models.shared import AmherstFields, INITIAL_FILTER_ARRAY2
from pawsupport.get_set import hash_simple_md5
from pycommence import FilterArray
from shipr.models import extended


class HireIn(sqm.SQLModel):
    __tablename__ = "hire"
    cmc_table_name: ClassVar[str] = "Hire"
    initial_filter_array: ClassVar[FilterArray] = sqm.Field(
        default=INITIAL_FILTER_ARRAY2,
        sa_column=sqm.Column(sqm.JSON)
    )
    record: dict = sqm.Field(sa_column=sqm.Column(sqm.JSON))
    state: Optional[BookingStateIn] = sqm.Field(None, sa_column=sqm.Column(sqm.JSON))

    input_address: Optional[extended.AddressRecipient] = sqm.Field(default=None, sa_column=sqm.Column(sqm.JSON))
    name: str = sqm.Field(default=None, unique=True, index=True)
    contact: Optional[extended.Contact] = sqm.Field(default=None, sa_column=sqm.Column(sqm.JSON))
    boxes: Optional[int] = None
    ship_date: Optional[date] = None

    # booking_state: BookingStateIn | None = sqm.Field(None, sa_column=Column(JSON))

    @property
    def get_hash(self):
        return hash_simple_md5([self.name, self.ship_date.isoformat()])

    @field_validator("name", mode="after")
    def name_is_none(cls, v, info):
        v = v or info.data.get("record").get(AmherstFields.NAME)
        return v

    @field_validator("boxes", mode="before")
    def boxes_is_none(cls, v, info):
        v = v if v is not None else info.data.get("record").get(AmherstFields.BOXES)
        if not v:
            v = 1
        return v

    @field_validator("input_address", "input_address", mode="after")
    def input_address_is_none(cls, v, info):
        v = v or extended.AddressRecipient(
            **addr_lines_dict_am(info.data.get("record").get(AmherstFields.ADDRESS)),
            town="",
            postcode=info.data.get("record").get(AmherstFields.POSTCODE),
        )
        return v

    @field_validator("contact", mode="after")
    def contact_is_none(cls, v, info):
        # todo check api reqs vis combinations of fields
        v = v or extended.Contact(
            business_name=info.data.get("record").get(AmherstFields.CUSTOMER),
            email_address=info.data.get("record").get(AmherstFields.EMAIL),
            mobile_phone=info.data.get("record").get(AmherstFields.TELEPHONE),
            contact_name=info.data.get("record").get(AmherstFields.CONTACT),
        )
        return v

    @field_validator("ship_date", mode="after")
    def ship_date_validate(cls, v, info):
        v = v or info.data.get("record").get("ship_date")
        tod = date.today()
        v = v if v and v > tod else tod
        return v

    @classmethod
    def records_to_sesh(cls, records: Sequence[dict[str, str]], session: sqm.Session):
        session.add_all([cls(record=record) for record in records])
        session.commit()


def addr_lines_dict_am(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([""] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ",".join(addr_lines[2:])
    return {f"address_line{num}": line for num, line in enumerate(addr_lines, start=1)}
