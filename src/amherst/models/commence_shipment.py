from __future__ import annotations

from datetime import datetime
from typing import ClassVar

from pydantic import Field
from shipaw.models.ship_types import ShipDirection

from amherst.models.amherst_base import AmherstBase, CommaSeparatedStrField
from amherst.models.commence_adaptors import CategoryName
from amherst.models.meta import register_table


def now_iso_seconds() -> str:
    return datetime.now().isoformat(timespec='seconds')


@register_table
class CommenceShipment(AmherstBase):
    category: ClassVar[CategoryName] = CategoryName.Shipment
    direction: ShipDirection = Field(..., alias='Direction')

    creation_datetime: str = Field(default_factory=now_iso_seconds, alias='Creation Datetime')
    name: str = Field(default_factory=now_iso_seconds, alias='Name')
    latest_tracking: str = Field('', alias='Latest Tracking')
    tracking_links: CommaSeparatedStrField = Field(default_factory=list, alias='Tracking Links')
    notes: str = Field('', alias='Notes')
    hire: CommaSeparatedStrField = Field('', alias='For Hire')
    sale: CommaSeparatedStrField = Field('', alias='For Sale')
    customer: CommaSeparatedStrField = Field('', alias='For Customer')
