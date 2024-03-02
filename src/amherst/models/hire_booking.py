# from __future__ import annotations

# if _ty.TYPE_CHECKING:
# ...

import sqlmodel as sqm
import sqlalchemy as sqa

from amherst.models import hire_model
from pawsupport.sqlmodel_ps import sqlpr
from shipr.models.ui_states import bookings, states


class HireBooking(bookings.BaseBooking):
    hire: hire_model.Hire = sqm.Field(sa_column=sqa.Column(sqlpr.GenericJSONType(hire_model.Hire)))
    state: states.ShipState = sqm.Field(
        sa_column=sqm.Column(sqlpr.GenericJSONType(states.ShipState))
    )

    # booking_date: dt.date = pyd.Field(default_factory=dt.date.today)


class HireBookingDB(HireBooking, table=True):
    id: int | None = sqm.Field(default=None, primary_key=True)


class HireBookingOut(HireBooking):
    id: int
