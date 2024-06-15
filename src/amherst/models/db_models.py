# from __future__ import annotations

import sqlmodel as sqm
from pawdantic.pawsql import required_json_field

from amherst.models.am_record import AmherstRecord, EmailOption
from shipaw.models.booking_states import BookingState


class BookingStateDB(BookingState, table=True):
    id: int | None = sqm.Field(default=None, primary_key=True)
    record: AmherstRecord = required_json_field(AmherstRecord)

    @property
    def email_options(self):
        if self.remote_contact and self.remote_contact.email_address not in [_.email for _ in
                                                                             self.record.email_options]:
            return self.record.email_options + [EmailOption(
                email=self.remote_contact.email_address,
                description='Entered',
                name='entered'
            )]
        return self.record.email_options

        # record_id: int | None = sqm.Field(default=None, foreign_key="amherstrecorddb.id")
    # record: AmherstRecordDB | None = sqm.Relationship(back_populates="booking_states")
