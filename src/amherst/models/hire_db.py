from datetime import date
from typing import ClassVar, Optional
from sqlalchemy.types import TypeDecorator

from pydantic import BaseModel, field_validator
from sqlmodel import Column, Field, JSON, SQLModel

from amherst.models.shared import AmherstFields, INITIAL_FILTER_ARRAY2
from pycommence import FilterArray
from shipr import types as elt
from shipr.express.types import AddressPFPartial


class Notifications(SQLModel):
    notification_type: list[str] = Field(default_factory=list, sa_column=Column(JSON))




class ContactType(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        return value.model_dump_json() if value is not None else ''

    def process_result_value(self, value, dialect):
        return ContactPFSQL.model_validate_json(value) if value else None

class AddressPartialType(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        return value.model_dump_json() if value is not None else ''

    def process_result_value(self, value, dialect):
        return AddressPFPartial.model_validate_json(value) if value else None


class AddressType(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        return value.model_dump_json() if value is not None else ''

    def process_result_value(self, value, dialect):
        return AddressPFPartial.model_validate_json(value) if value else None


class ContactPFSQL(BaseModel):
    business_name: str
    email_address: str
    mobile_phone: str

    # contact_name: Optional[str] = Field(None)
    # telephone: Optional[str] = Field(None)
    # fax: Optional[str] = Field(None)
    #
    # senders_name: Optional[str] = Field(None)
    # notifications: Optional[Notifications] = Field(None, sa_column=Column(JSON))


class HireDB(SQLModel, table=True):
    """ Primary Hire Type """
    __tablename__ = "hire"

    id: Optional[int] = Field(default=None, primary_key=True)

    initial_filter_array: ClassVar[FilterArray] = Field(
        default=INITIAL_FILTER_ARRAY2,
        sa_column=Column(JSON)
    )

    record: dict = Field(sa_column=Column(JSON))

    hire_address: Optional[elt.AddressPF] = Field(default=None, sa_column=Column(AddressType))
    hire_contact: Optional[ContactPFSQL] = Field(default=None, sa_column=Column(ContactType))
    boxes: Optional[int] = Field(default=None)
    ship_date: Optional[date] = Field(default=None)
    partial_address: Optional[AddressPFPartial] = Field(default=None, sa_column=Column(AddressPartialType))

    @field_validator("boxes", mode="before")
    def boxes_is_none(cls, v, info):
        v = v if v is not None else info.data.get('record').get(AmherstFields.BOXES)
        if not v:
            v = 1
        return v

    @field_validator('partial_address', mode="after")
    def address_is_none(cls, v, info):
        v = v or elt.AddressPFPartial(
            **addr_lines_dict(info.data.get('record').get(AmherstFields.ADDRESS)),
            postcode=info.data.get('record').get(AmherstFields.POSTCODE)
        )
        return v

    @field_validator('hire_contact', mode="after")
    def contact_is_none(cls, v, info):
        # todo check api reqs vis combinations of fields
        v = v or ContactPFSQL(
            business_name=info.data.get('record').get(AmherstFields.CUSTOMER),
            email_address=info.data.get('record').get(AmherstFields.EMAIL),
            mobile_phone=info.data.get('record').get(AmherstFields.TELEPHONE),
            # contact_name=info.data.get('record').get(AmherstFields.CONTACT),
        )
        return v

    # @model_validator(mode="after")
    # def address_contact(self):
    #     print(self.record.get('customer'))
    #     self.hire_contact = self.hire_contact if self.hire_contact is not None \
    #         else elt.ContactPF(
    #         business_name=self.record.get(AmherstFields.CUSTOMER),
    #         email_address=self.record.get(AmherstFields.EMAIL),
    #         mobile_phone=self.record.get(AmherstFields.TELEPHONE)
    #     )
    #     self.hire_address = self.hire_address if self.hire_address is not None \
    #         else elt.AddressPF(
    #         **addr_lines_dict(self.record.get(AmherstFields.ADDRESS)),
    #         town='', postcode=self.record.get(AmherstFields.POSTCODE)
    #     )
    #     return self

    # @field_validator("ship_date", mode="after")
    # def ship_date_validate(cls, v):
    #     v = v or v.record.get('ship_date')
    #     tod = date.today()
    #     v = v if v > tod else tod
    #     return v


# hire_shipping: Optional[parts.HireShipping] = Field(default=None, sa_column=Column(JSON))
# hire_dates: Optional[parts.HireDates] = Field(default=None, sa_column=Column(JSON))
# hire_status: Optional[parts.HireStatus] = Field(default=None, sa_column=Column(JSON))
# hire_payment: Optional[parts.HirePayment] = Field(default=None, sa_column=Column(JSON))
# hire_order: Optional[parts.HireOrder] = Field(default=None, sa_column=Column(JSON))
# hire_staff: Optional[parts.HireStaff] = Field(default=None, sa_column=Column(JSON))

# @field_validator("hire_dates", mode="after")
# def hire_dates_is_none(cls, v) -> parts.HireDates:
#     if v is None:
#         v =
#         return parts.HireDates()
#     return v
#
#
#
# def from_raw_cmc(cls, cmc_raw: HireRaw) -> Self:
#     submodels = {
#         'hire_dates': parts.HireDates,
#         'hire_status': parts.HireStatus,
#         'hire_shipping': parts.HireShipping,
#         'hire_address_am': AddressAm,
#         'hire_payment': parts.HirePayment,
#         'hire_order': parts.HireOrder,
#         'staff': parts.HireStaff,
#     }
#     out_dict = {}
#     for model_name, model_class in submodels.items():
#         out_dict[model_name] = sub_model_from_cmc(model_class, cmc_raw)
#     out_dict['name'] = cmc_raw.name
#     out_dict['customer'] = cmc_raw.customer
#
#     return cls.model_validate(out_dict)
#
def addr_lines(address: str) -> list[str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    return addr_lines


def addr_lines_dict(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    return {
        f'address_line{num}': line
        for num, line in enumerate(addr_lines, start=1)
    }
