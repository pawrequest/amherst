# from __future__ import annotations
from __future__ import annotations

import datetime as dt
import os

import fastapi
import sqlmodel as sqm
from fastui import FastUI, components as c, events, events as e
from loguru import logger

import shipr
from amherst import am_db, shipper
from amherst.front import booked, ship, support
from amherst.models import managers
from pawdantic.pawui import builders, pawui_types
from shipr.ship_ui import states

router = fastapi.APIRouter()


@router.get('/check_state/{man_id}', response_model=FastUI, response_model_exclude_none=True)
async def check_state(
        man_id: int,
        session=fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    man_in = await support.get_manager(man_id, session)
    texts = builders.dict_strs_texts(
        man_in.state.model_dump(exclude={'candidates'}),
        with_keys='YES'
    )
    return [
        c.Div(
            components=builders.list_of_divs(
                class_name='row my-2 mx-auto',
                components=texts
            ),
            class_name='row'
        )
    ]


@router.get(
    '/confirm/{manager_id}/{state_64}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def get_confirmation(
        manager_id: int,
        state_64: str,
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),
        session: sqm.Session = fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    state = states.ShipState.model_validate_64(state_64)
    state.candidates = pfcom.get_candidates(state.address.postcode)

    man_in = await support.get_manager(manager_id, session)
    man_in.state = state
    session.add(man_in)
    session.commit()
    session.refresh(man_in)
    return await confirm_book_page(man_in)


@router.get(
    '/go_book/{manager_id}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def do_booking(
        manager_id: int,
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),
        session: sqm.Session = fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    logger.warning(f'booking_id: {manager_id}')
    man_in = await support.get_manager(manager_id, session)

    if man_in.state.booking_state is not None:
        logger.error(f'booking {manager_id} already booked')
        alert_dict = {'ALREADY BOOKED': 'ERROR'}
        return await booked.booked_page(manager=man_in, alert_dict=alert_dict)

    try:
        if man_in.state.direction == 'in':
            tod = dt.date.today()
            if man_in.state.ship_date <= tod:
                raise shipr.ExpressLinkError('CAN NOT COLLECT TODAY')

        req, resp = await book_shipment(man_in, pfcom)
        processed_manager = await process_shipment(man_in, pfcom, req, resp)

        session.add(processed_manager)
        session.commit()
        man_out = managers.BookingManagerOut.model_validate(processed_manager)
        return await booked.booked_page(manager=man_out)

    except shipr.ExpressLinkError as e:
        alert_dict = {str(e): 'ERROR'}
        man_out = managers.BookingManagerOut.model_validate(man_in)

        return await ship.shipping_page(man_out.id, alert_dict=alert_dict)
        # return await shipping_page.hire_page(man_out, alert_dict=alert_dict)


async def book_shipment(manager, pfcom):
    req = pfcom.state_to_request(manager.state)
    logger.warning(f'BOOKING ({manager.state.direction.title()}) {manager.item.name}')
    resp = pfcom.get_shipment_resp(req)
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
    new_ship_state = manager.state.model_copy(update={'booking_state': booked_state})
    val_ship_state = shipr.ShipState.model_validate(new_ship_state)
    await support.wait_label2(val_ship_state, pfcom)
    os.startfile(val_ship_state.booking_state.label_dl_path)
    manager.state = val_ship_state
    return manager


async def confirm_book_page(
        manager: managers.MANAGER_IN_DB,
        alert_dict: pawui_types.AlertDict = None
) -> list[
    c.AnyComponent]:
    ret = await builders.page_w_alerts(
        # page_class_name='container-fluid',
        components=[
            c.Heading(
                text=f'Booking Confirmation for {manager.item.name}',
                level=1,
                class_name='row mx-auto my-5'
            ),
            c.ServerLoad(path=f'/book/check_state/{manager.id}'),
            await confirm_div(manager),
            await back_div(),
        ],
        title='booking',
        alert_dict=alert_dict,
    )
    return ret


async def back_div():
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                class_name='row btn btn-lg btn-primary',
                text='Back',
                on_click=events.GoToEvent(url='/ship/select/1'),
            )
        ]
    )


async def confirm_div(manager):
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                text='Confirm Booking',
                on_click=e.GoToEvent(url=f'/book/go_book/{manager.id}'),
                class_name='row btn btn-lg btn-primary'
            )
        ]
    )
