from __future__ import annotations

from abc import ABC
from datetime import datetime, date, time
from decimal import Decimal
from typing import Annotated, Optional, TypeVar, TYPE_CHECKING

from pydantic import BeforeValidator, BaseModel

from pycommence.entities import Connection

if TYPE_CHECKING:
    from amherst.commence_am.hire_cmc import HireCmc


def amherst_date_val(v):
    if not v:
        return None
    if isinstance(v, str):
        try:
            return datetime.strptime(v, '%d/%m/%Y').date()
        except ValueError:
            raise ValueError(f'Invalid date string: "{v}" - expecting amherst format dd/mm/yyyy')
    return v


def amherst_time_val(v):
    if not v:
        return None
    if isinstance(v, str):
        try:
            return datetime.strptime(v, '%H:%M').time()
        except ValueError:
            raise ValueError(f'Invalid time string: "{v}" - expecting amherst format HH:MM')
    return v

def list_from_string_comma(v):
    return v.split(',')


def list_from_string_newline(v):
    return v.split('\n')
def decimal_from_string(v):
    if not v:
        return Decimal(0)
    return Decimal(v)

DateAm = Annotated[date, BeforeValidator(amherst_date_val)]
DateMaybe = Annotated[Optional[date], BeforeValidator(amherst_date_val)]
TimeMaybe = Annotated[Optional[time], BeforeValidator(amherst_time_val)]
TimeAm = Annotated[time, BeforeValidator(amherst_time_val)]
ListComma = Annotated[list, BeforeValidator(list_from_string_comma)]
ListNewline = Annotated[list, BeforeValidator(list_from_string_newline)]
DecimalAm = Annotated[Decimal, BeforeValidator(decimal_from_string)]
T = TypeVar('T', bound=BaseModel)


def submodel_from_cmc[T](cls: type[T], cmc_obj: BaseModel) -> T:
    ob_dict = {
        attr: getattr(cmc_obj, attr) for attr in cls.model_fields
    }
    return cls.model_validate(ob_dict)


def submodel_from_cmc_prepend[T](cls: type[T], cmc_obj: HireCmc, prepend:str) -> T:
    ob_dict = {
        attr: getattr(cmc_obj, f'{prepend}{attr}') for attr in cls.model_fields
    }
    return cls.model_validate(ob_dict)


class CmcTable(BaseModel, ABC):
    class Config:
        extra = 'ignore'


class CmcConverted(BaseModel, ABC):
    class Config:
        extra = 'ignore'

    def from_cmc(self, cmc_obj: BaseModel) -> BaseModel:
        raise NotImplementedError


sale_customers = Connection(
    name='SaleCustomers',
    to_table='Customers',
    from_table='Sale',
)

HIRE_CUSTOMERS = Connection(
    name='HireCustomers',
    to_table='Customers',
    from_table='Hire',
)


class AmAddress(BaseModel):
    address: str
    contact: str
    email: str
    name: str
    postcode: str
    telephone: str
