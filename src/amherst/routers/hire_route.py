# from __future__ import annotations
import base64

import pydantic
from fastapi import APIRouter, Depends
from fastui import AnyComponent, FastUI, components as c
from fastui.events import GoToEvent
from loguru import logger
from sqlmodel import Session

import shipr.models.ui_states.states
from amherst.front.pages import hire_page
from amherst.models import hire_booking, hire_state
from amherst.am_db import get_hire_cursor, get_pfc, get_session
from amherst.hire_to_sesh import hire_record_to_session
from amherst.routers.booking_route import get_booking
from amherst.shipper import AmShipper
from pycommence import Csr

router = APIRouter()


@router.get(
    "/update/{booking_id}/{update_64}",
    response_model=FastUI,
    response_model_exclude_none=True
)
async def update_hire(
        booking_id: int,
        update_64: str | None = None,
        session: Session = Depends(get_session),
) -> list[AnyComponent]:
    try:
        upd = base64.urlsafe_b64decode(update_64).decode()
        updt = shipr.models.ui_states.states.ShipStatePartial.model_validate_json(upd)
    except pydantic.ValidationError as e:
        raise ValueError(
            f"update_64: {update_64} is not a valid base64 encoded ShipStatePartial\n{e}"
        )

    booking = await get_booking(booking_id, session)
    booking.state = booking.state.model_copy(
        update=updt.model_dump(exclude_none=True)
    )
    session.add(booking)
    session.commit()
    session.refresh(booking)
    page = hire_page.HirePage(booking=booking)
    return await page.get_page()
    # return [c.Text(text="Booking not found")]


@router.get("/view/{booking_id}", response_model=FastUI, response_model_exclude_none=True)
async def view_hire(
        booking_id: int,
        session: Session = Depends(get_session),
) -> list[AnyComponent]:
    booking = await get_booking(booking_id, session)
    page = hire_page.HirePage(booking=booking)
    return await page.get_page()


@router.get("/new/{hire_name}")
async def hire_from_cmc_name_64(
        hire_name: str,
        session=Depends(get_session),
        cursor: Csr = Depends(get_hire_cursor),
        pfcom: AmShipper = Depends(get_pfc),
):
    hire_name = base64.urlsafe_b64decode(hire_name).decode()
    logger.info(f"hire_name: {hire_name}")
    hire_record = cursor.get_record(hire_name)

    hire = hire_record_to_session(hire_record, session, pfcom)
    return [c.FireEvent(event=GoToEvent(url=f"/hire/view/{hire.id}"))]
