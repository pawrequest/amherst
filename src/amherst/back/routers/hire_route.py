# from __future__ import annotations
import base64
from typing import Optional

from fastui import AnyComponent, FastUI
from fastapi import APIRouter, Depends
from loguru import logger
from sqlmodel import select

from amherst.back.database import get_session
from amherst.front.hire_ui import HireUI as HireUI
from amherst.front.state import ShipState, state_from_hire
from amherst.back import get_pfc
from amherst.models import HireDB
from amherst.shipping.pfcom import AmShipper
from pawsupport.sqlmodel_ps import obj_in_session
from pycommence import csr_context

router = APIRouter()


@router.get("/id/{hire_id}", response_model=FastUI, response_model_exclude_none=True)
async def hire_view_id(
        hire_id: int,
        state: Optional[str] = None,
        session=Depends(get_session),
        pf_com: AmShipper = Depends(get_pfc),
) -> list[AnyComponent]:
    logger.info(f"hire_id: {hire_id}")
    hire = session.get(HireDB, hire_id)
    if state:
        state = ShipState.model_validate_json(state)
    else:
        state = state_from_hire(hire, pf_com)
    ui = HireUI(pfcom=pf_com, state=state)
    page = await ui.get_page()
    return page


@router.get("/{hire_name}", response_model=FastUI, response_model_exclude_none=True)
async def hire_view_name(
        hire_name: str,
        state: Optional[str] = None,
        pf_com: AmShipper = Depends(get_pfc),
        session=Depends(get_session)
) -> list[AnyComponent]:
    logger.info(f"hire_name: {hire_name}")

    hire_name = base64.urlsafe_b64decode(hire_name).decode()
    with csr_context('Hire') as csr:
        hire_record = csr.get_record(hire_name)
    hire = HireDB(record=hire_record)
    hire = HireDB.validate(hire)

    if not obj_in_session(session, hire, HireDB):
        session.add(hire)
        session.commit()
        session.refresh(hire)
    else:
        hire = session.exec(select(HireDB).where(HireDB.name == hire.name)).one()
        hire = HireDB.validate(hire)

    if state:
        state = ShipState.model_validate_json(state)
    else:
        state = state_from_hire(hire, pf_com)

    ui = HireUI(pfcom=pf_com, state=state)
    page = await ui.get_page()
    return page
