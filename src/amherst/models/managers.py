from __future__ import annotations

import datetime as dt

import sqlmodel as sqm

from shipr import types as s_types
from shipr.ship_ui import states
from . import hire_model


class BookingManager(sqm.SQLModel):
    state: states.ShipState
    item: hire_model.ShipableItem
    booking_date: dt.date


# def get_item_json_type(item: am_types.Shipable):
#     if isinstance(item, hire_model.Hire):
#         return sqm.Column(s_types.GenericJSONType(hire_model.Hire))
#     elif isinstance(item, sale_model.Sale):
#         return sqm.Column(s_types.GenericJSONType(sale_model.Sale))
#     else:
#         raise ValueError(f'item type not recognised: {item}')


# def get_shipable_db_type(item: am_types.ShipableType):
#     json_type = get_item_json_type(item)
#     return _t.Annotated[type(item), sqm.Field(sa_column=json_type)]


class BookingManagerDB(BookingManager, table=True):
    """subclass and set table = true"""
    id: int | None = sqm.Field(primary_key=True)
    state: states.ShipState = sqm.Field(
        sa_column=sqm.Column(s_types.GenericJSONType(states.ShipState))
    )
    item: hire_model.ShipableItem = sqm.Field(
        sa_column=sqm.Column(s_types.GenericJSONType(hire_model.ShipableItem))
    )
    booking_date: dt.date = sqm.Field(default_factory=dt.date.today)


class BookingManagerOut(BookingManager, table=False):
    id: int


BOOKED_MANAGER = BookingManagerDB | BookingManagerOut

#
#
# class GenericManager(sqm.SQLModel):
#     booking_date: dt.date = sqm.Field(default_factory=dt.date.today)
#     state: states.ShipState = sqm.Field(
#         sa_column=sqm.Column(s_types.GenericJSONType(states.ShipState))
#     )
#     item: BaseItem = sqm.Field(
#         sa_column=sqa.Column(s_types.GenericJSONType(BaseItem))
#     )
#
#
# class GenericManagerDB(GenericManager, table=True):
#     id: int | None = sqm.Field(default=None, primary_key=True)
#
#
# class GenericManagerOut(GenericManager):
#     id: int
#
#
# class HireManager(sqm.SQLModel):
#     booking_date: dt.date = sqm.Field(default_factory=dt.date.today)
#     state: states.ShipState = sqm.Field(
#         sa_column=sqm.Column(s_types.GenericJSONType(states.ShipState))
#     )
#     hire: hire_model.Hire = sqm.Field(
#         sa_column=sqa.Column(s_types.GenericJSONType(hire_model.Hire))
#     )
#
#
# class HireManagerDB(HireManager, table=True):
#     id: int | None = sqm.Field(default=None, primary_key=True)
#
#
# class HireManagerOut(HireManager):
#     id: int
#
#
# class SaleManager(sqm.SQLModel):
#     booking_date: dt.date = sqm.Field(default_factory=dt.date.today)
#     state: states.ShipState = sqm.Field(
#         sa_column=sqm.Column(s_types.GenericJSONType(states.ShipState))
#     )
#     sale: sale_model.Sale = sqm.Field(
#         sa_column=sqa.Column(s_types.GenericJSONType(sale_model.Sale))
#     )
#
#
# class SaleManagerDB(SaleManager, table=True):
#     id: int | None = sqm.Field(default=None, primary_key=True)
#
#
# class SaleManagerOut(SaleManager):
#     id: int
#
#
# GenericManager2 = _t.Union[HireManager, SaleManager]
