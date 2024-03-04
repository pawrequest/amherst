import datetime as dt

import sqlalchemy as sqa
import sqlmodel as sqm

from amherst.models import hire_model
from pawsupport import sqlpr
from shipr.ship_ui import managers, states


class HireManager(managers.BaseManager):
    hire: hire_model.Hire = sqm.Field(sa_column=sqa.Column(sqlpr.GenericJSONType(hire_model.Hire)))
    state: states.ShipState = sqm.Field(sa_column=sqm.Column(sqlpr.GenericJSONType(states.ShipState)))
    booking_date: dt.date = sqm.Field(default_factory=dt.date.today)


class HireManagerDB(HireManager, table=True):
    id: int | None = sqm.Field(default=None, primary_key=True)


class HireManagerOut(HireManager):
    id: int
