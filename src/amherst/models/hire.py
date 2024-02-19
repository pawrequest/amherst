from __future__ import annotations

from typing import Optional

from sqlmodel import Column, Field, JSON, SQLModel

from pycommence.filters import CmcFilterPy, FilterArray, FilterCondition
from .hire_parts import HireDates, HireItems, HirePayment, HireShipping, HireStaff, HireStatus
from .shared import (AmAddress, HireStatusEnum, MODEL_JSON)
from pycommence.models.cmc_models import CmcModel, sub_model_from_cmc
from .hire_cmc import HireCmc

INITIAL_FILTER_ARRAY1 = [
    CmcFilterPy(
        field_name='Status',
        condition=FilterCondition.EQUAL_TO,
        value=HireStatusEnum.BOOKED_IN,
    )
]

INITIAL_FILTER_ARRAY = FilterArray(
    CmcFilterPy(
        field_name='Status',
        condition=FilterCondition.EQUAL_TO,
        value=HireStatusEnum.BOOKED_IN,
    ),
)


class Hire(CmcModel, SQLModel):
    cmc_class = HireCmc
    initial_filter_array = INITIAL_FILTER_ARRAY

    name: str
    customer: str
    dates: HireDates
    status: HireStatus
    shipping: HireShipping
    delivery_address: AmAddress
    payment: HirePayment
    items: HireItems
    staff: HireStaff

    @property
    def contact_dict(self) -> dict[str, str]:
        return dict(
            business_name=self.customer,
            email_address=self.delivery_address.email,
            mobile_phone=self.delivery_address.telephone
        )

    @property
    def address_dict(self) -> dict[str, str]:
        add_lines = self.delivery_address.address.splitlines()

        if len(add_lines) > 3:
            add_lines[2] = ','.join(add_lines[2:])

        lines_dict = {
            f'address_line{num}': line
            for num, line in enumerate(add_lines, start=1)
        }

        return dict(
            **lines_dict,
            town=add_lines[-1],
            postcode=self.delivery_address.postcode,
        )

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




class HireTable(Hire, table=True):
    """ Primary Hire Type """
    id: Optional[int] = Field(default=None, primary_key=True)
    status: MODEL_JSON = Field(default=None, sa_column=Column(JSON))
    dates: MODEL_JSON = Field(default=None, sa_column=Column(JSON))
    shipping: MODEL_JSON = Field(default=None, sa_column=Column(JSON))
    delivery_address: MODEL_JSON = Field(default=None, sa_column=Column(JSON))
    payment: MODEL_JSON = Field(default=None, sa_column=Column(JSON))
    items: MODEL_JSON = Field(default=None, sa_column=Column(JSON))
    staff: MODEL_JSON = Field(default=None, sa_column=Column(JSON))

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
