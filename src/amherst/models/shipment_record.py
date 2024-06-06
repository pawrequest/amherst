from __future__ import annotations

import sqlmodel as sqm
from shipaw import ship_types as s_types
from shipaw.ship_ui import states

from .am_record import AmherstRecord


# class ShipmentRecord(sqm.SQLModel):
#     shipment: states.Shipment
#     record: AmherstRecord


class ShipmentRecord(sqm.SQLModel):
    shipment: states.Shipment
    record: AmherstRecord
    booking_state: states.BookingState | states.BookingState | None = None


class ShipmentRecordDB(ShipmentRecord, table=True):
    """subclass and set table = true"""

    id: int | None = sqm.Field(primary_key=True)
    shipment: states.Shipment = sqm.Field(
        sa_column=sqm.Column(s_types.PawdanticJSON(states.Shipment))
    )
    record: AmherstRecord = sqm.Field(sa_column=sqm.Column(s_types.PawdanticJSON(AmherstRecord)))
    booking_state: states.BookingState | None = sqm.Field(
        None,
        sa_column=sqm.Column(s_types.PawdanticJSON(states.BookingState))
    )


class ShipmentRecordOut(ShipmentRecord, table=False):
    id: int


ShipmentRecordInDB = ShipmentRecordDB | ShipmentRecordOut
