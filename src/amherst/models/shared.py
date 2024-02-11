from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime, time
from decimal import Decimal
from enum import StrEnum
from typing import Annotated, ClassVar, Optional, TYPE_CHECKING, Type, TypeVar

from pydantic import BaseModel, BeforeValidator, ValidationError

from pycommence.entities import Connection
from pycommence.wrapper.cmc_db import get_csr

if TYPE_CHECKING:
    pass


class FilterEnumAm(StrEnum):
    """

    """
    INITIAL_HIRE = '' # not closed. status in [Booked in, Booked in and packed, Partially packed] send method is parcelforce
    INITIAL_SALE = ''


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
        # v = v.split(' ')[0].strip()
        try:
            time_object = datetime.strptime(v, "%I:%M %p").time()
            return time_object
            # return datetime.strptime(v, '%H:%M').time()
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
    cmc_class: ClassVar[Type[CmcTable]]

    @classmethod
    @abstractmethod
    def from_cmc(cls, cmc_obj: BaseModel) -> CmcConverted:
        raise NotImplementedError

    @classmethod
    def from_name(cls, name: str) -> CmcConverted:
        csr = get_csr(cls.cmc_class.table_name)
        record = csr.get_record(name)
        cmc = cls.cmc_class(**record)
        return cls.from_cmc(cmc)

    @classmethod
    def from_record(cls, record: dict[str, str]) -> CmcConverted:
        try:
            cmc = cls.cmc_class(**record)
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
