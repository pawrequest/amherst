# from __future__ import annotations
import os
import pathlib
import time

import fastui
from fastui import components as c
import fastapi
import sqlmodel as sqm
from loguru import logger

from amherst.front import amui
from amherst import am_db, shipper
from amherst.front.pages import booked_page
from amherst.models import hire_booking
from amherst.models.hire_booking import HireBookingDB
from shipr.models.ui_states import states

router = fastapi.APIRouter()


@router.get("/dummy/")
async def dummy_page() -> list[fastui.AnyComponent]:
    print("pbboking opsted")
    return amui.Page.default_page(c.Text(text="dummy"))


@router.get("/go/{booking_id}", response_model=fastui.FastUI, response_model_exclude_none=True)
async def go(
        booking_id: int,
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),
        session: sqm.Session = fastapi.Depends(am_db.get_session),
) -> list[fastui.AnyComponent]:
    logger.warning(f"booking_id: {booking_id}")
    booking: HireBookingDB = await get_booking(booking_id, session)
    booking_out = hire_booking.HireBookingOut.model_validate(booking)

    if booking.state.book_state is not None:
        logger.error(f"booking {booking_id} already booked")
        ui = booked_page.PrintedPage(booking=booking_out)
        return await ui.get_page()

    req, resp = await book_hire(booking, pfcom)
    booked_state_ = await validate_booking(req, resp)
    label = await get_wait_label(booked_state_, pfcom)
    os.startfile(label)

    booking.state.book_state = booked_state_

    session.add(booking)
    session.commit()
    booking_out2 = hire_booking.HireBookingOut.model_validate(booking)

    return await booked_page.PrintedPage.from_booking(booking_out2)


async def validate_booking(req, resp) -> states.BookedState:
    return states.BookedState.model_validate(
        states.BookedState(
            request=req,
            response=resp,
        )
    )


async def book_hire(booking: hire_booking.HireBooking, pfcom):
    req = pfcom.state_to_shipment_request(booking.state)
    print(f'req: {req}')
    resp = pfcom.get_shipment_resp(req)
    print(f'resp: {resp}')
    return req, resp


async def get_booking(booking_id: int, session: sqm.Session) -> hire_booking.HireBookingDB:
    booking = session.get(hire_booking.HireBookingDB, booking_id)
    if not isinstance(booking, hire_booking.HireBookingDB):
        raise ValueError('booking not found')
    return booking


@router.get("/print/{booking_id}", response_model=fastui.FastUI, response_model_exclude_none=True)
async def print_label(
        booking_id: int,
        pfcom=fastapi.Depends(am_db.get_pfc),
        session=fastapi.Depends(am_db.get_session)
):
    logger.warning(f"printing id: {booking_id}")

    booking_in = await get_booking(booking_id, session)
    booking_out = hire_booking.HireBookingOut.model_validate(booking_in)
    if bstate := booking_out.state.book_state:
        if bstate.label_path:
            await prnt_label(booking_out.state.book_state)
        else:
            bstate.label_path = await get_wait_label(bstate, pfcom)
            os.startfile(bstate.label_path)
            booking_in.state = booking_in.state.model_copy(
                update={
                    "state.book_state.label_path": bstate.label_path,
                    "state.book_state.label_printed": True
                }
            )
    else:
        raise ValueError(f"booking {booking_id} has no booked state")

    session.add(booking_in)
    session.commit()
    session.refresh(booking_in)
    booking_out_2 = hire_booking.HireBookingOut.model_validate(booking_in)
    return await booked_page.PrintedPage.from_booking(booking=booking_out_2)


async def wait_label(label_path: pathlib.Path):
    while True:
        if not label_path:
            print("waiting for file to be created")
            time.sleep(1)
        else:
            break


async def get_wait_label(state: states.BookedState, pfcom):
    label_path = pfcom.get_label(state.shipment_num()).resolve()
    await wait_label(label_path)
    return label_path


async def prnt_label(state: states.BookedState) -> None:
    if not state.label_path.exists():
        logger.error(f"label_path {state.label_path} does not exist")
    os.startfile(state.label_path)
