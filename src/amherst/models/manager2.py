import datetime as dt
import typing as _t

import sqlmodel as sqm
from shipr.ship_ui import states
from shipr import types
import sqlalchemy as sqa

from amherst.models import hire_model, sale_model
from amherst.models.types import Shipable

T = _t.TypeVar('T', bound=Shipable)


class GenericManager(sqm.SQLModel):
    booking_date: dt.date = sqm.Field(default_factory=dt.date.today)
    state: states.ShipState = sqm.Field(
        sa_column=sqm.Column(types.GenericJSONType(states.ShipState))
    )
    item: T = sqm.Field(sa_column=sqa.Column(types.GenericJSONType(T)))


class GenericManagerDB(GenericManager, table=True):
    id: int | None = sqm.Field(default=None, primary_key=True)


class HireManager(sqm.SQLModel):
    booking_date: dt.date = sqm.Field(default_factory=dt.date.today)
    state: states.ShipState = sqm.Field(
        sa_column=sqm.Column(types.GenericJSONType(states.ShipState))
    )
    hire: hire_model.Hire = sqm.Field(sa_column=sqa.Column(types.GenericJSONType(hire_model.Hire)))


class HireManagerDB(HireManager, table=True):
    id: int | None = sqm.Field(default=None, primary_key=True)


class HireManagerOut(HireManager):
    id: int


class SaleManager(sqm.SQLModel):
    booking_date: dt.date = sqm.Field(default_factory=dt.date.today)
    state: states.ShipState = sqm.Field(
        sa_column=sqm.Column(types.GenericJSONType(states.ShipState))
    )
    sale: sale_model.Sale = sqm.Field(sa_column=sqa.Column(types.GenericJSONType(sale_model.Sale)))


class SaleManagerDB(SaleManager, table=True):
    id: int | None = sqm.Field(default=None, primary_key=True)


class SaleManagerOut(SaleManager):
    id: int


GenericManager2 = _t.Union[HireManager, SaleManager]
