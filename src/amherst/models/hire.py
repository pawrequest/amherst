from __future__ import annotations

from typing import Optional

from loguru import logger
from sqlmodel import Column, Field, JSON

from pycommence.filters import CmcFilter, FilterArray, FilterCondition
from .hire_parts import HireDates, HireItems, HirePayment, HireShipping, HireStaff, HireStatus
from .shared import (AddressAm, HireStatusEnum, MODEL_JSON)
from pycommence.models.cmc_models import CmcModel, sub_model_from_cmc
from .hire_cmc import HireCmc

INITIAL_FILTER_ARRAY1 = [
    CmcFilter(
        field_name='Status',
        condition=FilterCondition.EQUAL_TO,
        value=HireStatusEnum.BOOKED_IN,
    )
]

INITIAL_FILTER_ARRAY = FilterArray(
    CmcFilter(
        field_name='Status',
        condition=FilterCondition.EQUAL_TO,
        value=HireStatusEnum.BOOKED_IN,
    ),
    CmcFilter(
        field_name='Send Out Date',
        condition=FilterCondition.AFTER,
        value='2023-01-01',
    ),
)


class Hire(CmcModel):
    cmc_class = HireCmc
    initial_filter_array = INITIAL_FILTER_ARRAY

    name: str
    customer: str

    shipping: HireShipping
    dates: HireDates
    status: HireStatus
    delivery_address: AddressAm
    payment: HirePayment
    items: HireItems
    staff: HireStaff

    #
    # shipping: HireShipping = Field(default=None, sa_column=Column(JSON))
    # dates: HireDates = Field(default=None, sa_column=Column(JSON))
    # status: HireStatus = Field(default=None, sa_column=Column(JSON))
    # delivery_address: AmAddress = Field(default=None, sa_column=Column(JSON))
    # payment: HirePayment = Field(default=None, sa_column=Column(JSON))
    # items: HireItems = Field(default=None, sa_column=Column(JSON))
    # staff: HireStaff = Field(default=None, sa_column=Column(JSON))
    #
    # shipping: SerializeAsAny[HireShipping] = Field(default=None, sa_column=Column(JSON))
    # dates: SerializeAsAny[HireDates] = Field(default=None, sa_column=Column(JSON))
    # status: SerializeAsAny[HireStatus] = Field(default=None, sa_column=Column(JSON))
    # delivery_address: SerializeAsAny[AmAddress] = Field(default=None, sa_column=Column(JSON))
    # payment: SerializeAsAny[HirePayment] = Field(default=None, sa_column=Column(JSON))
    # items: SerializeAsAny[HireItems] = Field(default=None, sa_column=Column(JSON))
    # staff: SerializeAsAny[HireStaff] = Field(default=None, sa_column=Column(JSON))

    @classmethod
    def rout_prefix(cls) -> str:
        return '/hires/'

    @property
    def contact_dict(self) -> dict[str, str]:
        ret = dict(
            business_name=self.customer,
            email_address=self.delivery_address.email,
            mobile_phone=self.delivery_address.telephone
        )
        return ret


    @property
    def address_dict(self) -> dict[str, str]:
        try:
            # add = self.delivery_address.address.strip()
            add_lines = self.delivery_address.address.strip().splitlines()
            town = add_lines[-1]

            # if len(add_lines) < 3:
            #     add_lines.extend([''] * (3 - len(add_lines)))
            if len(add_lines) > 3:
                add_lines[2] = ','.join(add_lines[2:])

            lines_dict = {
                f'address_line{num}': line
                for num, line in enumerate(add_lines, start=1)
            }

            return dict(
                **lines_dict,
                town=town,
                postcode=self.delivery_address.postcode,
            )
        except AttributeError:
            logger.warning(f'Could not build address dict for hire "{self.name}"')
            return dict()

    @classmethod
    def from_cmc(cls, cmc_obj: HireCmc) -> Hire:
        return cls.model_validate(
            dict(
                name=cmc_obj.name,
                customer=cmc_obj.customer,
                dates=sub_model_from_cmc(HireDates, cmc_obj),
                status=sub_model_from_cmc(HireStatus, cmc_obj),
                shipping=sub_model_from_cmc(HireShipping, cmc_obj),
                delivery_address=sub_model_from_cmc(AddressAm, cmc_obj, prepend='delivery_'),
                payment=sub_model_from_cmc(HirePayment, cmc_obj),
                items=sub_model_from_cmc(HireItems, cmc_obj),
                staff=sub_model_from_cmc(HireStaff, cmc_obj),
            )
        )


class HireTable(Hire, table=True):
    """ Primary Hire Type """
    # model json simple dict now
    id: Optional[int] = Field(default=None, primary_key=True)
    dates: MODEL_JSON = Field(default=None, sa_column=Column(JSON))
    status: MODEL_JSON = Field(default=None, sa_column=Column(JSON))
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
