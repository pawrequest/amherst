from __future__ import annotations

import re
from datetime import datetime, date

from fastapi.encoders import jsonable_encoder


def sanitise_id(value):
    return re.sub(r'\W|^(?=\d)', '_', value).lower()


def make_jsonable(thing) -> dict:
    # todo remove this function and use jsonable_encoder directly in templates?!
    res = jsonable_encoder(thing)
    return res


def date_int_w_ordinal(n: int):
    """Convert an integer to its ordinal as a string, e.g. 1 -> 1st, 2 -> 2nd, etc."""
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def ordinal_dt(dt: datetime | date) -> str:
    """Convert a datetime or date to a string with an ordinal day, e.g. 'Mon 1st Jan 2020'."""
    return dt.strftime(f'%a {date_int_w_ordinal(dt.day)} %b %Y')
