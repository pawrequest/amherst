from __future__ import annotations

import datetime as dt

import sqlmodel as sqm

from shipaw import shipaw_types as s_types
from shipaw.ship_ui import states
from . import shipable_item


class BookingManager(sqm.SQLModel):
    state: states.ShipState
    item: shipable_item.ShipableItem
    booking_date: dt.date


class BookingManagerDB(BookingManager, table=True):
    """subclass and set table = true"""
    id: int | None = sqm.Field(primary_key=True)
    state: states.ShipState = sqm.Field(
        sa_column=sqm.Column(s_types.GenericJSONType(states.ShipState))
    )
    item: shipable_item.ShipableItem = sqm.Field(
        sa_column=sqm.Column(s_types.GenericJSONType(shipable_item.ShipableItem))
    )
    booking_date: dt.date = sqm.Field(default_factory=dt.date.today)


class BookingManagerOut(BookingManager, table=False):
    id: int


MANAGER_IN_DB = BookingManagerDB | BookingManagerOut

