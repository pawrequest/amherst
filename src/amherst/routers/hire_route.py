# from __future__ import annotations
import base64

from fastapi import APIRouter, Depends
from loguru import logger
from sqlmodel import Session

import amherst.front.pages.hp_2
import shipr
from amherst.am_db import get_hire_cursor, get_pfc, get_session
from amherst.front.pages import hp_2
from amherst.hire_to_sesh import hire_record_to_session
from amherst.models import hire_manager
from amherst.routers.booking_route import get_manager
from amherst.shipper import AmShipper
from fastui import FastUI
from fastui import components as c
from fastui.events import GoToEvent
from pycommence import Csr
from shipr.ship_ui import states

router = APIRouter()


@router.get('/neighbours/{booking_id}', response_model=FastUI, response_model_exclude_none=True)
async def neighbours(
    booking_id: int,
    pfcom: AmShipper = Depends(get_pfc),
    session: Session = Depends(get_session),
):
    man_in = await get_manager(booking_id, session)
    man_out = hire_manager.HireManagerOut.model_validate(man_in)
    postcode = man_in.hire.input_address.postcode
    candidates = pfcom.get_candidates(postcode)
    return await amherst.front.pages.hp_2.address_chooser(manager=man_out, candidates=candidates)


@router.get('/pcneighbours/{booking_id}/{postcode}', response_model=FastUI, response_model_exclude_none=True)
async def pcneighbours(
    booking_id: int,
    postcode: str,
    pfcom: AmShipper = Depends(get_pfc),
    session: Session = Depends(get_session),
):
    man_in = await get_manager(booking_id, session)
    man_out = hire_manager.HireManagerOut.model_validate(man_in)
    candidates = pfcom.get_candidates(postcode)
    return await amherst.front.pages.hp_2.address_chooser(manager=man_out, candidates=candidates)


@router.get('/update/{booking_id}/{update_64}', response_model=FastUI, response_model_exclude_none=True)
async def update_hire(
    booking_id: int,
    update_64: str | None = None,
    session: Session = Depends(get_session),
) -> list[c.AnyComponent]:
    updt = states.ShipStatePartial.model_validate_64(update_64)

    man_in = await get_manager(booking_id, session)
    man_out = hire_manager.HireManagerOut.model_validate(man_in)

    updated_state_ = man_out.state.get_updated(updt)
    updated_state = shipr.ShipState.model_validate(updated_state_)
    man_in.state = updated_state
    # man_out = hire_manager.HireManagerDB.model_validate(man_in)
    session.add(man_in)
    session.commit()
    session.refresh(man_in)
    return await hp_2.hire_page(manager=man_in)

    # return [c.Text(text="Booking not found")]


@router.get('/view/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def view_hire(
    manager_id: int,
    session: Session = Depends(get_session),
) -> list[c.AnyComponent]:
    man_in = await get_manager(manager_id, session)
    man_out = hire_manager.HireManagerOut.model_validate(man_in)
    if not man_out:
        raise ValueError(f'manager id {manager_id} not found')
    return await hp_2.hire_page(manager=man_out)


@router.get('/new/{hire_name}')
async def hire_from_cmc_name_64(
    hire_name: str,
    session=Depends(get_session),
    cursor: Csr = Depends(get_hire_cursor),
    pfcom: AmShipper = Depends(get_pfc),
):
    hire_name = base64.urlsafe_b64decode(hire_name).decode()
    logger.info(f'hire_name: {hire_name}')
    hire_record = cursor.get_record(hire_name)

    hire = hire_record_to_session(hire_record, session, pfcom)
    return [c.FireEvent(event=GoToEvent(url=f'/hire/view/{hire.id}'))]
