# from __future__ import annotations

# if _ty.TYPE_CHECKING:
#     pass

import sqlmodel as sqm

import shipr.models.ui_states.states
from amherst.models import hire_model


def hire_record_to_session(record: dict, session: sqm.Session, pfcom) -> hire_model.Hire:
    """Create a new hire and state in the database from a record dict."""
    hire_ = hire_model.Hire(record=record)
    state = shipr.models.ui_states.states.ShipState.hire_initial(hire_, pfcom)
    hire_.state = state
    hire = hire_model.Hire.model_validate(hire_)
    session.add(hire)
    session.commit()
    session.refresh(hire)
    return hire
