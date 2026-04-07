from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from amherst_core.consts_enums import CategoryName
from pycommence.core.meta import CommenceTable
from pycommence.core.types import (
    CommenceDateMaybe,
    CommencePath,
    CommenceString,
    CSVLines,
    CSVSpaces,
)
from pydantic import Field
from shipaw.utils.consts_enums import ShipDirection

from amherst.models.amherst_base import AmherstBase
from amherst.models.meta import register_table


def ordinal_day(n: int):
    """Convert an integer to its ordinal as a string, e.g. 1 -> 1st, 2 -> 2nd, etc."""
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def now_iso_seconds() -> str:
    return datetime.now().isoformat(timespec='seconds')


def ordinal_date_name() -> str:
    """sortable and human readable dt eg '2024-June-1st (Saturday @ 14:30:00)'"""
    dt = datetime.now()
    return dt.strftime(f'%Y-%B-{ordinal_day(dt.day)} (%A @ %H:%M:%S)')


class CommenceShipment(AmherstBase, CommenceTable):
    category: ClassVar[CategoryName] = CategoryName.Shipment
    direction: ShipDirection = Field(..., alias='Direction')
    label: CommencePath | None = Field(None, alias='Label')
    boxes: int = Field(0, alias='Boxes')
    send_date: CommenceDateMaybe = Field(..., alias='Send Date')
    collection_id: CommenceString = Field('', alias='Collection ID')

    creation_datetime: CommenceString = Field(default_factory=now_iso_seconds, alias='Creation Datetime')
    name: CommenceString = Field(default_factory=ordinal_date_name, alias='Name')
    latest_tracking: CommenceString = Field('', alias='Latest Tracking')
    tracking_links: CSVLines = Field(default_factory=list, alias='Tracking Links')
    shipment_numbers: CSVSpaces = Field(default_factory=list, alias='Shipment Numbers')
    notes: CommenceString = Field('', alias='Notes')

    hires: CSVSpaces = Field(default_factory=list, alias='For Hire')
    sales: CSVSpaces = Field(default_factory=list, alias='For Sale')
    customers: CSVSpaces = Field(default_factory=list, alias='For Customer')
