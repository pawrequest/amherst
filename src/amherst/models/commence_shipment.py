from __future__ import annotations

from datetime import datetime, date
from typing import ClassVar

from pydantic import Field
from shipaw.models.ship_types import ShipDirection

from amherst.models.amherst_base import AmherstBase, CommaSeparatedStrField
from amherst.models.commence_adaptors import CategoryName
from amherst.models.meta import register_table


def date_int_w_ordinal(n: int):
    """Convert an integer to its ordinal as a string, e.g. 1 -> 1st, 2 -> 2nd, etc."""
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def ordinal_dt(dt: datetime | date) -> str:
    """Convert a datetime or date to a string with an ordinal day, e.g. 'Mon 1st Jan 2020'."""
    return dt.strftime(f'%Y-%B-{date_int_w_ordinal(dt.day)} (%A @ %H:%M:%S)')


def now_iso_seconds() -> str:
    return datetime.now().isoformat(timespec='seconds')


def now_iso_seconds2() -> str:
    return ordinal_dt(datetime.now())


@register_table
class CommenceShipment(AmherstBase):
    category: ClassVar[CategoryName] = CategoryName.Shipment
    direction: ShipDirection = Field(..., alias='Direction')

    creation_datetime: str = Field(default_factory=now_iso_seconds, alias='Creation Datetime')
    name: str = Field(default_factory=now_iso_seconds2, alias='Name')
    latest_tracking: str = Field('', alias='Latest Tracking')
    tracking_links: CommaSeparatedStrField = Field(default_factory=list, alias='Tracking Links')
    notes: str = Field('', alias='Notes')
    hire: CommaSeparatedStrField = Field('', alias='For Hire')
    sale: CommaSeparatedStrField = Field('', alias='For Sale')
    customer: CommaSeparatedStrField = Field('', alias='For Customer')
