# from typing import Optional
#
# from sqlmodel import SQLModel, Field
#
#
# class HireStateLink(SQLModel, table=True):
#     hire_id: Optional[int] = Field(default=None, foreign_key="hire.id", primary_key=True)
#     state_id: Optional[int] = Field(default=None, foreign_key="hirestate.id", primary_key=True)
