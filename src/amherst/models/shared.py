from __future__ import annotations

import json
from datetime import date, datetime, time
from decimal import Decimal
from enum import StrEnum
from typing import Any, Optional, TYPE_CHECKING, TypeVar

from loguru import logger
from pydantic import AfterValidator, BaseModel, BeforeValidator, PlainSerializer, SerializeAsAny
from typing_extensions import Annotated
from fastapi.encoders import jsonable_encoder
from pycommence.entities import Connection
from pydantic import Json
if TYPE_CHECKING:
    pass


class FilterEnumAm(StrEnum):
    """

    """
    INITIAL_HIRE = ''  # not closed. status in [Booked in, Booked in and packed, Partially packed] send method is parcelforce
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
        try:
            if 'AM' in v or 'PM' in v:
                time_object = datetime.strptime(v, "%I:%M %p").time()
            else:
                time_object = datetime.strptime(v, '%H:%M').time()
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


def model_with_sub(model, jsonify=False) -> dict | str:
    out = {}
    for attr, value in model.model_dump().items():
        if isinstance(value, BaseModel):
            out[attr] = model_with_sub(value)
        else:
            out[attr] = value
    if jsonify:
        return json.dumps(out)
    return out


def model_with_sub_json2(model) -> dict | str:
    try:
        out = {}
        for attr, value in model.model_dump().items():
            if isinstance(value, BaseModel):
                out[attr] = model_with_sub(value)
            else:
                out[attr] = value
        return json.dumps(out)
    except Exception as e:
        logger.error(f'Error in model_with_sub_json: {e}')


def model_with_sub_json(model) -> Any:
    # json_compatible_item_data = jsonable_encoder(model)
    # return json.dumps(json_compatible_item_data)

    # return model.model_dump_json()
    return json.dumps(model_with_sub(model))


HireDatesAm = Annotated[BaseModel, BeforeValidator(amherst_date_val)]

DateAm = Annotated[date, BeforeValidator(amherst_date_val)]
DateMaybe = Annotated[Optional[date], BeforeValidator(amherst_date_val)]
TimeMaybe = Annotated[Optional[time], BeforeValidator(amherst_time_val)]
TimeAm = Annotated[time, BeforeValidator(amherst_time_val)]
ListComma = Annotated[list, BeforeValidator(list_from_string_comma)]
ListNewline = Annotated[list, BeforeValidator(list_from_string_newline)]
DecimalAm = Annotated[Decimal, BeforeValidator(decimal_from_string)]
T = TypeVar('T', bound=BaseModel)
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


class ContactAm(BaseModel):
    email: str
    name: str
    telephone: str


class AddressAm(BaseModel):
    address: str
    contact: str
    email: str
    # name: str
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


MODEL_JSON = dict
MODEL_JSON3 = Annotated[
    dict, PlainSerializer(model_with_sub_json)
    ]

MODEL_JSON2 = Annotated[BaseModel, PlainSerializer(lambda v: v.model_dump_json())]
