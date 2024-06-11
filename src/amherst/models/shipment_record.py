from __future__ import annotations

import sqlmodel as sqm

from shipaw import BookingState, Shipment, ship_types as s_types
from .am_record import AmherstRecord


# class ShipmentRecord(sqm.SQLModel):
#     shipment: Shipment
#     record: AmherstRecord


class ShipmentRecord(sqm.SQLModel):
    shipment: Shipment
    record: AmherstRecord
    booking_state: BookingState | None = None


class ShipmentRecordDB(ShipmentRecord, table=True):
    """subclass and set table = true"""

    id: int | None = sqm.Field(primary_key=True)
    shipment: Shipment = sqm.Field(sa_column=sqm.Column(s_types.PawdanticJSON(Shipment)))
    record: AmherstRecord = sqm.Field(sa_column=sqm.Column(s_types.PawdanticJSON(AmherstRecord)))
    booking_state: BookingState | None = sqm.Field(
        None,
        sa_column=sqm.Column(s_types.PawdanticJSON(BookingState))
    )


# class BookingStateDB(BookingState, table=True):
#     id: int | None = sqm.Field(primary_key=True)
#
#
# class AmRecordDB(AmherstRecord, table=True):
#     id: int | None = sqm.Field(primary_key=True)


class ShipmentRecordOut(ShipmentRecord, table=False):
    id: int


ShipmentRecordInDB = ShipmentRecordDB | ShipmentRecordOut
