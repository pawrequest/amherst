# import datetime as dt
#
# import sqlalchemy as sqa
# import sqlmodel as sqm
#
# from amherst.models import hire_model
# from shipr.models.types import GenericJSONType
# from shipr.ship_ui import managers, states
#
#
# class HireManager(managers.BaseManager):
#     hire: hire_model.Hire = sqm.Field(sa_column=sqa.Column(GenericJSONType(hire_model.Hire)))
#     state: states.ShipState = sqm.Field(
#         sa_column=sqm.Column(GenericJSONType(states.ShipState))
#     )
#     booking_date: dt.date = sqm.Field(default_factory=dt.date.today)
#
#
# class HireManagerDB(HireManager, table=True):
#     id: int | None = sqm.Field(default=None, primary_key=True)
#
#
# class HireManagerOut(HireManager):
#     id: int
