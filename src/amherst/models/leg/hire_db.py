#
# from typing import Optional
#
# from sqlalchemy import Column, JSON
# from sqlmodel import Field, Relationship
#
# from amherst.front.hire_ui import HireState
# from amherst.models import Hire
#
#
# class HireDB(Hire, table=True):
#     """ Primary Hire Type """
#     # model json simple dict now
#     __tablename__ = "hire"
#
#     id: Optional[int] = Field(default=None, primary_key=True)
#     dates: dict = Field(default=None, sa_column=Column(JSON))
#     status: dict = Field(default=None, sa_column=Column(JSON))
#     shipping: dict = Field(default=None, sa_column=Column(JSON))
#     delivery_address: dict = Field(default=None, sa_column=Column(JSON))
#     payment: dict = Field(default=None, sa_column=Column(JSON))
#     items: dict = Field(default=None, sa_column=Column(JSON))
#     staff: dict = Field(default=None, sa_column=Column(JSON))
#
#     state_id: Optional[int] = Field(default=None, foreign_key="hire_state.id", unique=True)
#     # state: Optional['HireStateDB'] = Relationship(back_populates="hire")
#
#     @classmethod
#     def rout_prefix(cls) -> str:
#         return '/hire/'
#
#
# class HireStateDB(HireState, table=True):
#     __tablename__ = "hire_state"
#     id: Optional[int] = Field(default=None, primary_key=True)
#     hire_id: Optional[int] = Field(default=None, foreign_key="hire.id", unique=True)
#     # hire: Optional[HireDB] = Relationship(back_populates="hire_state")
