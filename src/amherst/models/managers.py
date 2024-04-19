from __future__ import annotations

import sqlmodel as sqm
from shipaw import ship_types as s_types
from shipaw.ship_ui import states

from . import shipable_item


class BookingManager(sqm.SQLModel):
    state: states.ShipState
    record: shipable_item.ShipableRecord


class BookingManagerDB(BookingManager, table=True):
    """subclass and set table = true"""

    id: int | None = sqm.Field(primary_key=True)
    state: states.ShipState = sqm.Field(sa_column=sqm.Column(s_types.GenericJSONType(states.ShipState)))
    record: shipable_item.ShipableRecord = sqm.Field(
        sa_column=sqm.Column(s_types.GenericJSONType(shipable_item.ShipableRecord))
    )


class BookingManagerOut(BookingManager, table=False):
    id: int


MANAGER_IN_DB = BookingManagerDB | BookingManagerOut
