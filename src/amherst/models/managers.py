from __future__ import annotations

import datetime as dt
from enum import Enum

import pydantic as _p
import sqlmodel as sqm
from shipaw import ship_types as s_types
from shipaw.ship_ui import states

from . import am_shared, shipable_item
from ..am_types import AmherstTableName


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


class BookingManager2(sqm.SQLModel):
    state: states.ShipState
    record: dict[str, str]
    cmc_table_name: AmherstTableName

    @_p.computed_field
    def field_enum(self) -> type[Enum]:
        return getattr(am_shared, self.cmc_table_name + 'Fields')

    def from_record(self, key: str):
        return self.record.get(self.field_enum[key])


class BookingManager2DB(BookingManager2, table=True):
    """subclass and set table = true"""
    id: int | None = sqm.Field(primary_key=True)
    state: states.ShipState = sqm.Field(
        sa_column=sqm.Column(s_types.GenericJSONType(states.ShipState))
    )
    record: dict[str, str] = sqm.Field(sa_column=sqm.Column(sqm.JSON))
    cmc_table_name: AmherstTableName = sqm.Field(sa_column=sqm.Column(sqm.JSON))


class BookingManagerOut2(BookingManager, table=False):
    id: int


MANAGER_IN_DB2 = BookingManager2DB | BookingManagerOut2
