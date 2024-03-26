# from __future__ import annotations
import datetime as dt
import os
import pathlib
import time

import fastapi
import fastui
import pdf_tools
import sqlmodel as sqm
from loguru import logger

import shipr
from amherst import am_db, shipper
from amherst.front.pages import booked_pages, shipping_page
from amherst.models import managers
from amherst.routers.back_funcs import get_manager
from shipr.ship_ui import states

router = fastapi.APIRouter()


@router.get('/view/{manager_id}', response_model=fastui.FastUI, response_model_exclude_none=True)
async def view_booked(
        manager_id: int,
        session: sqm.Session = fastapi.Depends(am_db.get_session),
) -> list[fastui.AnyComponent]:
    manager = await get_manager(manager_id, session)
    manager_ = managers.BookingManagerOut.model_validate(manager)
    return await booked_pages.booked_page(manager=manager_)
    # return await builders.page_w_alerts(
    #     components=[
    #         builders.back_link,
    #     ],
    # )


@router.get(
    '/confirm/{manager_id}/{state_64}',
    response_model=fastui.FastUI,
    response_model_exclude_none=True
)
async def get_confirmation(
        manager_id: int,
        state_64: str,
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),
        session: sqm.Session = fastapi.Depends(am_db.get_session),
) -> list[fastui.AnyComponent]:
    state = states.ShipState.model_validate_64(state_64)
    state.candidates = pfcom.get_candidates(state.address.postcode)

    man_in = await get_manager(manager_id, session)
    man_in.state = state
    session.add(man_in)
    session.commit()
    session.refresh(man_in)
    return await booked_pages.confirm_book_page(man_in)


@router.get(
    '/go_book/{manager_id}',
    response_model=fastui.FastUI,
    response_model_exclude_none=True
)
async def do_booking(
        manager_id: int,
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),
        session: sqm.Session = fastapi.Depends(am_db.get_session),
) -> list[fastui.AnyComponent]:
    logger.warning(f'booking_id: {manager_id}')
    man_in = await get_manager(manager_id, session)

    if man_in.state.booking_state is not None:
        logger.error(f'booking {manager_id} already booked')
        alert_dict = {'ALREADY BOOKED': 'ERROR'}
        return await booked_pages.booked_page(manager=man_in, alert_dict=alert_dict)

    try:
        if man_in.state.direction == 'in':
            tod = dt.date.today()
            if man_in.state.ship_date <= tod:
                raise shipr.ExpressLinkError('CAN NOT COLLECT TODAY')

        req, resp = await book_shipment(man_in, pfcom)
        booked_man = await process_shipment(man_in, pfcom, req, resp)

        session.add(booked_man)
        session.commit()
        man_out = managers.BookingManagerOut.model_validate(booked_man)
        return await booked_pages.booked_page(manager=man_out)

    except shipr.ExpressLinkError as e:
        alert_dict = {str(e): 'ERROR'}
        man_out = managers.BookingManagerOut.model_validate(man_in)

        return await shipping_page.ship_page(man_out, alert_dict=alert_dict)
        # return await shipping_page.hire_page(man_out, alert_dict=alert_dict)



@router.get('/email/{booking_id}', response_model=fastui.FastUI, response_model_exclude_none=True)
async def email_label(
        booking_id: int,
        pfcom=fastapi.Depends(am_db.get_pfc),
        session=fastapi.Depends(am_db.get_session)
):
    logger.warning(f'printing id: {booking_id}')
    man_in = await get_manager(booking_id, session)
    send_label(man_in)


@router.get('/print/{booking_id}', response_model=fastui.FastUI, response_model_exclude_none=True)
async def print_label(
        booking_id: int,
        pfcom=fastapi.Depends(am_db.get_pfc),
        session=fastapi.Depends(am_db.get_session)
):
    logger.warning(f'printing id: {booking_id}')

    man_in = await get_manager(booking_id, session)

    booked = man_in.state.booking_state
    if not booked.label_path:
        booked.label_path = await wait_label(booked.shipment_num(), pfcom)
        session.add(man_in)
        session.commit()

    await prnt_label(booked.label_path)

    return await booked_pages.booked_page(manager=man_in)



async def book_shipment(manager, pfcom, direction=None):
    direction = direction or manager.state.direction
    if direction == 'out':
        req = pfcom.state_to_shipment_request(manager.state)
        action = 'SHIPMENT'
    elif direction == 'in':
        req = pfcom.state_to_collection_request(manager.state)
        action = 'COLLECTION'
    else:
        raise ValueError(f'Invalid booking type: {direction}')

    print(f'req: {req}')
    logger.warning(f'BOOKING {action} {manager.item.name}')
    resp = pfcom.get_shipment_resp(req)
    print(f'resp: {resp}')

    return req, resp


async def book_inbound(manager: managers.BookingManager, pfcom: shipper.AmShipper):
    req = pfcom.state_to_collection_request(manager.state)
    print(f'req: {req}')
    logger.warning(f'BOOKING COLLECTION {manager.item.name}')
    resp = pfcom.get_shipment_resp(req)
    print(f'resp: {resp}')
    return req, resp


async def process_shipment(
        manager: managers.BookingManagerDB,
        pfcom: shipper.AmShipper,
        req,
        resp,
):
    if not resp.completed_shipment_info:
        raise shipr.ExpressLinkError(str(states.response_alert_dict(resp)))

    booked_state = states.BookingState.model_validate(dict(request=req, response=resp))
    label = await wait_label(booked_state.shipment_num(), pfcom)
    os.startfile(label)
    state_ = manager.state.model_copy(update={'booking_state': booked_state})
    state = shipr.ShipState.model_validate(state_)
    manager.state = state
    return manager


async def validated_book_state(req, resp) -> states.BookingState:
    return states.BookingState.model_validate(
        states.BookingState(
            request=req,
            response=resp,
        )
    )


def create_email(man_in):
    pass


def send_label(man_in):
    email = create_email(man_in)
    pass

async def wait_label(ship_num: str, pfcom: shipper.AmShipper):
    label_path = pfcom.get_label(ship_num).resolve()

    for i in range(20):
        if label_path:
            return label_path
        else:
            print('waiting for file to be created')
            time.sleep(1)
    else:
        raise ValueError(f'file not created after 20 seconds {label_path=}')


async def prnt_label(label_path: pathlib.Path) -> None:
    if not label_path.exists():
        logger.error(f'label_path {label_path} does not exist')

    pdf_tools.array_pdf.convert_many(label_path, print_files=True)
