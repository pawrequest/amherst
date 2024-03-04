# from __future__ import annotations

import datetime as dt

import sqlmodel as sqm
import sqlalchemy as sqa

import shipr.ui_states.abc
from pawsupport.sqlmodel_ps import sqlpr


# if _ty.TYPE_CHECKING:
#     pass


class SStae(shipr.ui_states.abc.BaseUIState):
    id: int | None = None


class Hiring(sqm.SQLModel):
    record: dict[str, str]
    ship_date: dt.date | None = None


class Booking(sqm.SQLModel, table=True):
    id: int | None = sqm.Field(primary_key=True)
    hire: Hiring = sqm.Field(
        sa_column=sqa.Column(
            sqlpr.GenericJSONType(Hiring)
        )
    )
    state: SStae = sqm.Field(
        sa_column=sqm.Column(sqlpr.GenericJSONType(SStae))
    )


def test_ss(test_session):
    booking = Booking(
        hire=Hiring(
            record={"send_out_date": "01/01/2022"},
            ship_date=dt.date(2024, 3, 7),
        ),
        state=SStae(
        )
    )
    test_session.add(booking)
    test_session.commit()
    test_session.refresh(booking)
    # assert booking.id
    # assert booking.hire.ship_date == dt.date(2024, 3, 7)
    # assert booking.state.ship_date == dt.date(2024, 3, 7)
