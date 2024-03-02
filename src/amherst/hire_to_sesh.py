# from __future__ import annotations

# if _ty.TYPE_CHECKING:
#     pass

import sqlmodel as sqm

import shipr.models.ui_states.states
from amherst.models import hire_model, hire_state


def hire_record_to_session(record: dict, session: sqm.Session, pfcom) -> hire_in.Hire:
    """Create a new hire and state in the database from a record dict."""
    hire_ = hire_in.Hire(record=record)
    state = shipr.models.ui_states.states.ShipState.hire_initial(hire_, pfcom)
    hire_.state = state
    hire = hire_in.Hire.model_validate(hire_)
    session.add(hire)
    session.commit()
    session.refresh(hire)
    return hire
