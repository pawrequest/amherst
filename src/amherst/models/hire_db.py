from datetime import date
from typing import ClassVar, Optional

from pydantic import field_validator
from sqlmodel import Column, Field, JSON, SQLModel

from amherst.models.shared import AmherstFields, INITIAL_FILTER_ARRAY2
from amherst.models.types import AddressType, ContactType
from pawsupport.get_set import hash_simple_md5
from pycommence import FilterArray
from shipr.models import pf_types as elt


class HireDB(SQLModel, table=True):
    """ Primary Hire Type """
    __tablename__ = "hire"
    cmc_table_name: ClassVar[str] = "Hire"
    id: Optional[int] = Field(default=None, primary_key=True)
    initial_filter_array: ClassVar[FilterArray] = Field(
        default=INITIAL_FILTER_ARRAY2,
        sa_column=Column(JSON)
    )

    record: dict = Field(sa_column=Column(JSON))

    name: Optional[str] = Field(default=None, unique=True)
    address: Optional[elt.AddressPF] = Field(default=None, sa_column=Column(AddressType))
    contact: Optional[elt.ContactPF] = Field(default=None, sa_column=Column(ContactType))
    boxes: Optional[int] = Field(default=None)
    ship_date: Optional[date] = Field(default=None)

    @property
    def get_hash(self):
        return hash_simple_md5([self.name, self.ship_date.isoformat()])

    @field_validator("name", mode="after")
    def name_is_none(cls, v, info):
        v = v or info.data.get('record').get(AmherstFields.NAME)
        return v

    @field_validator("boxes", mode="before")
    def boxes_is_none(cls, v, info):
        v = v if v is not None else info.data.get('record').get(AmherstFields.BOXES)
        if not v:
            v = 1
        return v

    @field_validator('address', mode="after")
    def address_is_none(cls, v, info):
        v = v or elt.AddressPF(
            **addr_lines_dict_am(info.data.get('record').get(AmherstFields.ADDRESS)),
            town='', postcode=info.data.get('record').get(AmherstFields.POSTCODE)
        )
        return v

    @field_validator('contact', mode="after")
    def contact_is_none(cls, v, info):
        # todo check api reqs vis combinations of fields
        v = v or elt.ContactPF(
            business_name=info.data.get('record').get(AmherstFields.CUSTOMER),
            email_address=info.data.get('record').get(AmherstFields.EMAIL),
            mobile_phone=info.data.get('record').get(AmherstFields.TELEPHONE),
            contact_name=info.data.get('record').get(AmherstFields.CONTACT),
        )
        return v

    @field_validator("ship_date", mode="after")
    def ship_date_validate(cls, v, info):
        v = v or info.data.get('record').get('ship_date')
        tod = date.today()
        v = v if v and v > tod else tod
        return v


def addr_lines_dict_am(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    return {
        f'address_line{num}': line
        for num, line in enumerate(addr_lines, start=1)
    }
