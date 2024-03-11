from __future__ import annotations

import json
import typing as _t
from datetime import date, datetime, time
from decimal import Decimal
from typing import Optional, TypeVar

from pydantic import BaseModel, BeforeValidator, PlainSerializer

from amherst.models import hire_model, sale_model


def amherst_date_val(v):
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
                time_object = datetime.strptime(v, '%I:%M %p').time()
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


HireDatesAm = _t.Annotated[BaseModel, BeforeValidator(amherst_date_val)]
MODEL_JSON = dict
MODEL_JSON2 = _t.Annotated[BaseModel, PlainSerializer(lambda v: v.model_dump_json())]
DateAm = _t.Annotated[date, BeforeValidator(amherst_date_val)]
DateMaybe = _t.Annotated[Optional[date], BeforeValidator(amherst_date_val)]
TimeMaybe = _t.Annotated[Optional[time], BeforeValidator(amherst_time_val)]
TimeAm = _t.Annotated[time, BeforeValidator(amherst_time_val)]
ListComma = _t.Annotated[list, BeforeValidator(list_from_string_comma)]
ListNewline = _t.Annotated[list, BeforeValidator(list_from_string_newline)]
DecimalAm = _t.Annotated[Decimal, BeforeValidator(decimal_from_string)]
Shipable = _t.Union[hire_model.Hire, sale_model.Sale]
ShipableType = TypeVar('ShipableType', bound=Shipable)
