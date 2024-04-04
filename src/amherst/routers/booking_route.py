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
from amherst.front.pages import booked_pages, ship_page_2
from amherst.models import managers
from amherst.routers.back_funcs import get_manager
from shipr.ship_ui import states
from suppawt.office_ps.email_handler import Email
from suppawt.office_ps.ms.outlook_handler import OutlookHandler

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
        processed_manager = await process_shipment(man_in, pfcom, req, resp)

        session.add(processed_manager)
        session.commit()
        man_out = managers.BookingManagerOut.model_validate(processed_manager)
        return await booked_pages.booked_page(manager=man_out)

    except shipr.ExpressLinkError as e:
        alert_dict = {str(e): 'ERROR'}
        man_out = managers.BookingManagerOut.model_validate(man_in)

        return await ship_page_2.shipping_page(man_out.id, alert_dict=alert_dict)
        # return await shipping_page.hire_page(man_out, alert_dict=alert_dict)


@router.get('/email/{booking_id}', response_model=fastui.FastUI, response_model_exclude_none=True)
async def email_label(
        booking_id: int,
        pfcom=fastapi.Depends(am_db.get_pfc),
        session=fastapi.Depends(am_db.get_session)
):
    logger.warning(f'printing id: {booking_id}')
    man_in = await get_manager(booking_id, session)
    send_label(man_in.state)
    return await booked_pages.booked_page(manager=man_in)


@router.get('/print/{booking_id}', response_model=fastui.FastUI, response_model_exclude_none=True)
async def print_label(
        booking_id: int,
        session=fastapi.Depends(am_db.get_session)
):
    logger.warning(f'printing id: {booking_id}')
    man_in = await get_manager(booking_id, session)
    if not man_in.state.booking_state.label_downloaded:
        raise ValueError('label not downloaded')
    await prnt_label(man_in.state.booking_state.label_dl_path)
    return await booked_pages.booked_page(manager=man_in)


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
    await wait_label2(val_ship_state, pfcom)
    os.startfile(val_ship_state.booking_state.label_dl_path)
    manager.state = val_ship_state
    return manager


def send_label(state: shipr.ShipState):
    email = Email(
        to_address=state.contact.email_address,
        subject='Radio Hire - Parcelforce Collection Label Attached',
        body='Please find attached the Parcelforce Collection Label for your Radio Hire',
        attachment_path=state.booking_state.label_dl_path,
    )
    handler = OutlookHandler()
    handler.send_email(email)


def get_named_labelpath(state: shipr.ShipState):
    pdir = os.environ.get('PARCELFORCE_LABELS_DIR')
    stt = f'Parcelforce Collection Label for {state.contact.business_name} on {state.ship_date}'
    return pathlib.Path(pdir) / f'{stt}.pdf'


async def wait_label(ship_num: str, pfcom: shipper.AmShipper):
    label_path = pfcom.get_label(ship_num=ship_num).resolve()

    for i in range(20):
        if label_path:
            return label_path
        else:
            print('waiting for file to be created')
            time.sleep(1)
    else:
        raise ValueError(f'file not created after 20 seconds {label_path=}')


async def wait_label2(state: shipr.ShipState, pfcom: shipper.AmShipper) -> bool:
    label_path = pfcom.get_label(
        ship_num=state.booking_state.shipment_num(),
        dl_path=state.named_label_path if state.direction == 'in' else None,
    ).resolve()

    for i in range(20):
        if label_path:
            state.booking_state.label_downloaded = True
            state.booking_state.label_dl_path = label_path
            return True
        else:
            print('waiting for file to be created')
            time.sleep(1)
    else:
        raise ValueError(f'file not created after 20 seconds {label_path=}')


async def prnt_label(label_path: pathlib.Path) -> None:
    if not label_path.exists():
        logger.error(f'label_path {label_path} does not exist')

    pdf_tools.array_pdf.convert_many(label_path, print_files=True)
