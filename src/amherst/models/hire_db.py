from typing import Optional

from sqlmodel import Field, Relationship

from amherst.models.hire_state import HireState
from shipr.models.booking_state import BookingStateUpdater
from amherst.models.hire_in import HireIn
from amherst.models.links import HireStateLink


class Hire(HireIn, table=True):
    """Primary Hire Type"""

    id: Optional[int] = Field(default=None, primary_key=True)
    state: Optional["HireState"] = Relationship(back_populates="hire", link_model=HireStateLink)

    def update_hire_state(self, booking_update: BookingStateUpdater, session):
        state = self.state.update(booking_update)
        self.state = state
        session.add_all([self, state])
        session.commit()
        session.refresh(self, state)
        return self
