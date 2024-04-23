from __future__ import annotations

import sqlmodel as sqm

from shipaw import ship_types as s_types
from shipaw.ship_ui import states
from .am_record import AmherstRecord


class BookingManager(sqm.SQLModel):
    state: states.ShipState
    record: AmherstRecord


class BookingManagerDB(BookingManager, table=True):
    """subclass and set table = true"""

    id: int | None = sqm.Field(primary_key=True)
    state: states.ShipState = sqm.Field(sa_column=sqm.Column(s_types.PawdanticJSON(states.ShipState)))
    record: AmherstRecord = sqm.Field(sa_column=sqm.Column(s_types.PawdanticJSON(AmherstRecord)))


class BookingManagerOut(BookingManager, table=False):
    id: int


MANAGER_IN_DB = BookingManagerDB | BookingManagerOut
