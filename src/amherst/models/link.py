import sqlmodel as sqm


class RecordStateLink(sqm.SQLModel, table=True):
    __tablename__ = "record_state_link"
    amrec_id: int | None = sqm.Field(default=None, foreign_key='amherst_record.id', primary_key=True)
    booking_state_id: int | None = sqm.Field(default=None, foreign_key='booking_state.id')
