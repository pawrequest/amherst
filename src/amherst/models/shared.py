from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime, time
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, ClassVar, Optional, TYPE_CHECKING, Type, TypeVar

from pycommence import CmcDB
from pydantic import BaseModel, BeforeValidator, ValidationError
from pycommence.entities import Connection

if TYPE_CHECKING:
    pass


def amherst_date_val(v):
    if not v:
        return None
    if isinstance(v, str):
        try:
            return datetime.strptime(v, '%d/%m/%Y').date()
        except ValueError:
            try:
                return datetime.strptime(v, '%m/%d/%Y').date()
            except ValueError:
                raise ValueError(
                    f'Invalid date string: "{v}" - expecting amherst format dd/mm/yyyy or mm/dd/yyyy'
                )
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
    try:
        v = v.strip()
        v = v.replace(',', '')
        v = v.replace('%', '')
        v = v.replace('£', '')
        return Decimal(v)
    except ValueError:
        raise ValueError(f'Invalid decimal string: "{v}"')
    except ValidationError as e:
        raise ValueError(f'Failed to parse decimal: "{v}"') from e

DateAm = Annotated[date, BeforeValidator(amherst_date_val)]
DateMaybe = Annotated[Optional[date], BeforeValidator(amherst_date_val)]
TimeMaybe = Annotated[Optional[time], BeforeValidator(amherst_time_val)]
TimeAm = Annotated[time, BeforeValidator(amherst_time_val)]
ListComma = Annotated[list, BeforeValidator(list_from_string_comma)]
ListNewline = Annotated[list, BeforeValidator(list_from_string_newline)]
DecimalAm = Annotated[Decimal, BeforeValidator(decimal_from_string)]
T = TypeVar('T', bound=BaseModel)


def submodel_from_cmc[T](cls: type[T], cmc_obj: CmcTable | CmcConverted, *, prepend: str = '') -> T:
    ob_dict = {
        attr: getattr(cmc_obj, f'{prepend}{attr}') for attr in cls.model_fields
    }
    return cls.model_validate(ob_dict)


def submodel_from_cmc_prepend[T](cls: type[T], cmc_obj: CmcTable, prepend: str = '') -> T:
    ob_dict = {
        attr: getattr(cmc_obj, f'{prepend}{attr}') for attr in cls.model_fields
    }
    return cls.model_validate(ob_dict)


class CmcTable(BaseModel, ABC):
    table_name: ClassVar[str]

    class Config:
        extra = 'ignore'


class CmcConverted(BaseModel, ABC):
    converted_class: ClassVar[Type[CmcTable]]

    @classmethod
    @abstractmethod
    def from_cmc(cls, cmc_obj: BaseModel) -> CmcConverted:
        raise NotImplementedError

    @classmethod
    def from_name(cls, name: str) -> CmcConverted:
        db = CmcDB()
        cursor = db.get_cursor(cls.converted_class.table_name)
        record = cursor.get_record_one(name)
        cmc = cls.converted_class(**record)
        return cls.from_cmc(cmc)

    @classmethod
    def from_record(cls, record: dict[str, str]) -> CmcConverted:
        try:
            cmc = cls.converted_class(**record)
            return cls.from_cmc(cmc)
        except ValidationError as e:
            raise ValueError(f'Failed to convert record to {cls.__name__}') from e


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


class HireStatusEnum(StrEnum):
    BOOKED_IN = 'Booked in'
    PACKED = 'Booked in and packed'
    PARTIALLY_PACKED = 'Partially packed'
    OUT = 'Out'
    RTN_OK = 'Returned all OK'
    RTN_PROBLEMS = 'Returned with problems'
    QUOTE_GIVEN = 'Quote given'
    CANCELLED = 'Cancelled'
    EXTENDED = 'Extended'
    SOLD = 'Sold To Customer'
