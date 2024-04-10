from __future__ import annotations

import datetime as dt
import os
import typing as _t

import fastapi
import sqlmodel as sqm
from fastapi import responses
from fastui import FastUI, components as c, events, events as e
from fastui.forms import fastui_form
from loguru import logger

import shipr
from amherst import am_db, shipper
from amherst.front import booked, ship, support
from amherst.models import managers
from pawdantic.pawui import builders, pawui_types
from shipr.ship_ui import states, states as ship_states

router = fastapi.APIRouter()


@router.post('/confirm_post/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def confirm_post(
        manager_id: int,
        form: _t.Annotated[
            ship_states.ShipStatePartial, fastui_form(ship_states.ShipStatePartial)],
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),
        session=fastapi.Depends(am_db.get_session),

):
    update = ship_states.ShipStatePartial.model_validate(form.model_dump())
    if update.address.postcode:
        update.candidates = pfcom.get_candidates(update.address.postcode)
    await support.update_and_commit(manager_id, update, session)
    return responses.RedirectResponse(url=f'/ship/select/{manager_id}')


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
    """Endpoint returning Booking Confirmation Page.

    Args:
        manager_id (int): BookingManager id.
        state_64 (str): State as Base64 encoded JSON.
        pfcom (shipper.AmShipper, optional): The shipper object - defaults to fastapi.Depends(amherst.am_db.get_pfc).
        session (sqm.Session, optional): The database session - defaults to fastapi.Depends(amherst.am_db.get_session).

    Returns:
        c.Page: :meth:`~confirm_book_page`

    """
    state = states.ShipState.model_validate_64(state_64)
    state.candidates = pfcom.get_candidates(state.address.postcode)

    man_in = await support.get_manager(manager_id, session)
    man_in.state = state
    session.add(man_in)
    session.commit()
    session.refresh(man_in)
    return await confirm_book_page(man_in)


async def confirm_book_page(
        manager: managers.MANAGER_IN_DB,
        alert_dict: pawui_types.AlertDict = None
) -> list[
    c.AnyComponent]:
    """Confirmation page.

    Args:
        manager (managers.MANAGER_IN_DB): The manager object.
        alert_dict (pawui_types.AlertDict, optional): The alert dictionary - defaults to None.

    Returns:
        c.Page: Pre-Confirmation page.

    """
    return await builders.page_w_alerts(
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
    """Endpoint for booking a shipment.

    Args:
        manager_id (int): The manager's id.
        pfcom (shipper.AmShipper, optional): The shipper object - defaults to fastapi.Depends(amherst.am_db.get_pfc).
        session (sqm.Session, optional): The database session - defaults to fastapi.Depends(amherst.am_db.get_session).

    Returns:
        c.Page:
        - :meth:`~amherst.front.booked.booked_page`: Post-Booking Page on success.
        - :meth:`~amherst.front.ship.shipping_page`: Shipping Page on failure, which may include alerts.

    """
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

        return await ship.shipping_page(man_out.id, session=session, alert_dict=alert_dict)


@router.get('/check_state/{man_id}', response_model=FastUI, response_model_exclude_none=True)
async def check_state(
        man_id: int,
        session=fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    """Html Div with the current state of the manager.

    Args:
        man_id (int): The BookingManger id.
        session (sqm.Session, optional): The database session - defaults to fastapi.Depends(am_db.get_session).

    Returns:
        list(c.Div): A list containing a single DIV with each attribute of state as a text element.

    """
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


async def book_shipment(manager: managers.MANAGER_IN_DB, pfcom: shipper.AmShipper):
    """Book a shipment.

    Args:
        manager (managers.BookingManagerDB): The :class:`~managers.MANAGER_IN_DB` object.
        pfcom (shipper.AmShipper): :class:`~shipper.AmShipper` object.

    Returns:
        tuple: The request and response objects.

    """
    req = pfcom.state_to_request(manager.state)
    logger.warning(f'BOOKING ({manager.state.direction.title()}) {manager.item.name}')
    resp = pfcom.shipment_req_to_resp(req)
    return req, resp


async def process_shipment(
        manager: managers.BookingManagerDB,
        pfcom: shipper.AmShipper,
        req,
        resp,
):
    """Process the shipment.

    Args:
        manager (managers.BookingManagerDB): The manager object.
        pfcom (shipper.AmShipper): :class:`~shipper.AmShipper` object.
        req: The request object.
        resp: The response object.

    Returns:
        managers.BookingManagerDB: The manager object.

    """
    if not resp.completed_shipment_info:
        raise shipr.ExpressLinkError(str(states.response_alert_dict(resp)))

    booked_state = states.BookingState.model_validate(dict(request=req, response=resp))
    new_ship_state = manager.state.model_copy(update={'booking_state': booked_state})
    val_ship_state = shipr.ShipState.model_validate(new_ship_state)
    await support.wait_label2(val_ship_state, pfcom)
    os.startfile(val_ship_state.booking_state.label_dl_path)
    manager.state = val_ship_state
    return manager


async def back_div():
    """Back button."""
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
    """Confirm button."""
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
