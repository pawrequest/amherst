# from __future__ import annotations
import os
import pathlib
import time

import fastapi
import sqlmodel as sqm
from loguru import logger
import fastuipr
import shipr
from fastuipr import components as c
from shipr.ship_ui import states, managers
from pawsupport import pdf_tools

from amherst import am_db, shipper
from amherst.front import amui
from amherst.front.pages import booked_pages
from amherst.models import managers

router = fastapi.APIRouter()


@router.get('/dummy/')
async def dummy_page() -> list[fastuipr.AnyComponent]:
    print('dummy page got')
    return amui.Page.default_page(c.Text(text='dummy'))


@router.get('/go/{manager_id}', response_model=fastuipr.FastUI, response_model_exclude_none=True)
async def go(
        manager_id: int,
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),
        session: sqm.Session = fastapi.Depends(am_db.get_session),
) -> list[fastuipr.AnyComponent]:
    logger.warning(f'booking_id: {manager_id}')
    manager = await get_manager(manager_id, session)

    if manager.state.booking_state is not None:
        logger.error(f'booking {manager_id} already booked')
        return await booked_pages.booked_page(manager=manager)

    req, resp = await book_hire(manager, pfcom)
    booked_state_ = await validated_book_state(req, resp)
    label = await get_wait_label(booked_state_, pfcom)
    os.startfile(label)
    state_ = manager.state.model_copy(update={'booking_state': booked_state_})
    state = shipr.ShipState.model_validate(state_)

    manager.state = state

    session.add(manager)
    session.commit()
    session.refresh(manager)

    return await booked_pages.booked_page(manager=manager)


async def validated_book_state(req, resp) -> states.BookingState:
    return states.BookingState.model_validate(
        states.BookingState(
            request=req,
            response=resp,
        )
    )


async def book_hire(manager: managers.BookingManager, pfcom):
    req = pfcom.state_to_shipment_request(manager.state)
    print(f'req: {req}')
    logger.warning(f'BOOKING SHIPMENT {manager.item.name}')
    resp = pfcom.get_shipment_resp(req)
    print(f'resp: {resp}')
    return req, resp


async def get_manager(manager_id: int, session: sqm.Session) -> managers.BookingManagerDB:
    man_in = session.get(managers.BookingManagerDB, manager_id)
    if not isinstance(man_in, managers.BookingManagerDB):
        raise ValueError('booking not found')
    return man_in


async def get_manager1(manager_id: int, session: sqm.Session) -> managers.BookingManagerDB:
    man_in = session.get(managers.BookingManagerDB, manager_id)
    if not isinstance(man_in, managers.BookingManagerDB):
        raise ValueError('booking not found')
    return man_in


@router.get('/print/{booking_id}', response_model=fastuipr.FastUI, response_model_exclude_none=True)
async def print_label(
        booking_id: int,
        pfcom=fastapi.Depends(am_db.get_pfc),
        session=fastapi.Depends(am_db.get_session)
):
    logger.warning(f'printing id: {booking_id}')

    manager = await get_manager(booking_id, session)
    if booked := manager.state.booking_state:
        if booked.label_path:
            await prnt_label(booked.label_path)
        else:
            booked.label_path = await get_wait_label(booked, pfcom)
            await prnt_label(booked.label_path)

            #
            # os.startfile(booked.label_path)
            # manager.state = manager.state.model_copy(
            #     update={
            #         'state.book_state.label_path': booked.label_path,
            #         'state.book_state.label_printed': True
            #     }
            # )
    else:
        raise ValueError(f'booking {booking_id} has no booked state')

    session.add(manager)
    session.commit()
    session.refresh(manager)
    return await booked_pages.printed_page(manager=manager)


async def wait_label(label_path: pathlib.Path):
    while True:
        if not label_path:
            print('waiting for file to be created')
            time.sleep(1)
        else:
            break


async def get_wait_label(state: states.BookingState, pfcom):
    label_path = pfcom.get_label(state.shipment_num()).resolve()
    await wait_label(label_path)
    return label_path


async def prnt_label(label_path: pathlib.Path) -> None:
    if not label_path.exists():
        logger.error(f'label_path {label_path} does not exist')

    pdf_tools.array_pdf.convert_many(label_path, print_files=True)
    os.startfile(label_path)
    ...
