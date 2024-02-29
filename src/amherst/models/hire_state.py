from typing import Optional, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .hire_db import Hire
from .links import HireStateLink
from shipr.models.booking_state import BookingStateIn


class HireState(BookingStateIn, SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    # hire_id: int = Field(foreign_key="hire.id", unique=True, index=True)
    hire: "Hire" = Relationship(back_populates="state", link_model=HireStateLink)
