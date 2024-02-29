from __future__ import annotations

from sqlmodel import Session

from amherst.models import Hire, BookingState


def hire_record_to_session(record: dict, session: Session, pfcom) -> Hire:
    """Create a new hire and state in the database from a record dict."""
    hire = Hire(record=record)
    hire = Hire.model_validate(hire)
    state = BookingState.hire_initial(hire, pfcom)
    state = state.model_validate(state)
    session.add(state)
    session.commit()
    session.refresh(hire)
    return hire
