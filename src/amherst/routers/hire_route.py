# from __future__ import annotations
import base64

from fastapi import APIRouter, Depends
from fastui import AnyComponent, FastUI, components as c
from fastui.events import GoToEvent
from loguru import logger
from sqlmodel import Session

from amherst.database import get_hire_cursor, get_pfc, get_session
from amherst.front import amui
from amherst.hire_to_sesh import hire_record_to_session
from amherst.front.pages import HirePage
from amherst.models import Hire
from shipr.models.booking_state import BookingStateIn, BookingStateUpdater
from amherst.shipper import AmShipper
from pycommence import Csr

router = APIRouter()


@router.get("/view/{hire_id}", response_model=FastUI, response_model_exclude_none=True)
async def view_hire(
    hire_id: int,
    session: Session = Depends(get_session),
    updater: str | None = None,
    pfcom: AmShipper = Depends(get_pfc),
) -> list[AnyComponent]:
    hire = session.get(Hire, hire_id)
    if not isinstance(hire, Hire):
        logger.error(f"{hire_id=} not found")
        raise ValueError(f"hire_id: {hire_id} not found")
    # logger.info(f"view hire_id: {hire_id}/n{hire.state=}")
    if updater:
        updater_ = BookingStateUpdater.model_validate_json(updater)
        state = hire.state.update(updater_)
        session.add(hire)
        session.commit()
        session.refresh(hire)
    else:
        state = BookingStateIn.hire_initial(hire, pfcom)
    ui = HirePage(state=state)
    return await ui.get_page()


@router.get("/update_/{hire_id}", response_model=FastUI, response_model_exclude_none=True)
async def update_state(hire_id: int, updater: str, session=Depends(get_session)) -> list[AnyComponent]:
    logger.warning(updater)
    return [amui.Row.empty()]
    # updater = BookingStateUpdater.model_validate_json(q)
    # hire = session.get(hire_id)
    # hire.state = hire.state.update(updater)
    # hire = hire.model_validate(hire)
    #
    # session.add(hire)
    # session.commit()
    # return await view_hire(hire_id=hire.id, session=session)


@router.get("/new/{hire_name}")
async def hire_from_cmc_name_64(
    hire_name: str,
    session=Depends(get_session),
    cursor: Csr = Depends(get_hire_cursor),
    pfcom: AmShipper = Depends(get_pfc),
):
    logger.info(f"get hire_name64: {hire_name}")
    hire_name = base64.urlsafe_b64decode(hire_name).decode()
    logger.info(f"hire_name: {hire_name}")
    hire_record = cursor.get_record(hire_name)

    hire = hire_record_to_session(hire_record, session, pfcom)
    return [c.FireEvent(event=GoToEvent(url=f"/hire/id/{hire.id}"))]


async def update_hire_state(hire_id, session, updater: BookingStateUpdater):
    hire = session.get(Hire, hire_id)
    if not isinstance(hire, Hire):
        raise ValueError(f"hire_id: {hire_id} not found")
    state = hire.state.update(updater)
    hire.state = state
    session.add_all([hire, state])
    session.commit()
    session.refresh(hire, state)
    return hire


# @router.get("/name/{hire_name}")
# async def hire_view_name(hire_name: str, pf_com: AmShipper = Depends(get_pfc), session=Depends(get_session)) -> list[AnyComponent]:
#     logger.info(f"hire_name: {hire_name}")
#     hire_name = base64.urlsafe_b64decode(hire_name).decode()
#     if hire := session.exec(select(HireDB).where(HireDB.name == hire_name)).one_or_none():
#         hire = hire.model_validate(hire)
#     else:
#         hire = await hire_from_cmc_by_name(hire_name, session)
#
#     state = state_from_hire(hire, pf_com)
#
#     ui = HirePage(pfcom=pf_com, state=state)
#     page = await ui.get_page()
#     return page
