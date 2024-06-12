# from __future__ import annotations

import sqlmodel as sqm

from amherst.models.am_record import AmherstRecordDB
from shipaw.models.booking_states import BookingState


class BookingStateDB(BookingState, table=True):
    id: int | None = sqm.Field(default=None, primary_key=True)
    record_id: int | None = sqm.Field(default=None, foreign_key="amherstrecorddb.id")
    record: AmherstRecordDB | None = sqm.Relationship(back_populates="booking_states")
