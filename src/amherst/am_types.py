from __future__ import annotations

import typing as _t
from datetime import datetime
from decimal import Decimal

from amherst.models import am_shared


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


AmherstTableName = _t.Literal['Hire', 'Sale', 'Customer']
AmherstFieldsEnumType = am_shared.HireFields | am_shared.SaleFields | am_shared.CustomerFields
