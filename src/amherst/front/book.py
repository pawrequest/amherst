"""
Pages and Endpoints for Booking Shipments.
"""
from __future__ import annotations

import datetime as dt
import os

import fastapi
import sqlmodel as sqm
from fastui import FastUI, components as c, events, events as e
from loguru import logger
from pawdantic.pawui import builders, pawui_types
import shipaw
from pycommence import PyCommence
from shipaw import ELClient
from shipaw.ship_ui import states as ship_states

from amherst import am_db
from amherst.front import booked, ship, support
from amherst.front.support import update_manager_state
from amherst.models.shipment_record import ShipmentRecordDB, ShipmentRecordInDB, ShipmentRecordOut

router = fastapi.APIRouter()


@router.get(
    '/confirm/{manager_id}/{state_64}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def confirm_or_back(
        manager_id: int,
        state_64: str,
        pfcom: ELClient = fastapi.Depends(am_db.get_el_client),
        session: sqm.Session = fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    """Endpoint to submit state and return 'Confirm or Back' page.

    Args:
        manager_id (int): BookingManager id.
        state_64 (str): State as Base64 encoded JSON.
        pfcom (ELClient, optional): The shipper object - defaults to fastapi.Depends(amherst.am_db.get_pfc).
        session (sqm.Session, optional): The database session - defaults to fastapi.Depends(amherst.am_db.get_session).

    Returns:
        c.Page: :meth:`~confirm_book_page`

    """
    state = ship_states.Shipment.model_validate_64(state_64)
    state.candidates = pfcom.get_candidates(state.address.postcode)

    man_in = await update_manager_state(manager_id, session, state)
    return await confirm_or_back_page(man_in)


async def confirm_or_back_page(
        manager: ShipmentRecordInDB, alert_dict: pawui_types.AlertDict = None
) -> list[c.AnyComponent]:
    """Confirm or Back page.

    Display the current state and buttons to proceed with booking or go back.

    Args:
        manager (managers.MANAGER_IN_DB): The manager object.
        alert_dict (pawui_types.AlertDict, optional): The alert dictionary - defaults to None.

    Returns:
        c.Page: Pre-Confirmation page.

    """
    return await builders.page_w_alerts(
        components=[
            c.Heading(
                text=f'Booking Confirmation for {manager.record.name}',
                level=1,
                class_name='row mx-auto my-5'
            ),
            c.ServerLoad(path=f'/book/check_state/{manager.id}'),
            await confirm_div(manager),
            await back_div(manager.id),
        ],
        title='booking',
        alert_dict=alert_dict,
    )


def record_tracking(man_in: ShipmentRecordInDB):
    tracking_number = man_in.shipment.booking_state.response.shipment_num
    category = man_in.record.cmc_table_name
    record_name = man_in.record.name
    direction = man_in.shipment.direction

    py_cmc = PyCommence.from_table_name(table_name=category)
    tracking_field = 'Tracking Inbound' if direction == 'in' else 'Tracking Outbound'
    tracking_link_field = 'Track Inbound' if direction == 'in' else 'Track Outbound'

    pf_url = 'https://www.parcelforce.com/track-trace?trackNumber='

    existing_tracking = man_in.record.tracking_in if direction == 'in' else man_in.record.tracking_out
    tracking = ','.join(
        [existing_tracking, tracking_number]
    ) if existing_tracking else tracking_number

    tracking_link = pf_url + tracking_number

    py_cmc.edit_record(
        record_name,
        {tracking_field: tracking, tracking_link_field: tracking_link, 'DB label printed': True}
    )
    logger.info(f'Updated {tracking_field} for {record_name} to {tracking}\nand {tracking_link_field} to {tracking_link}')


@router.get('/go_book/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def do_booking(
        manager_id: int,
        pfcom: ELClient = fastapi.Depends(am_db.get_el_client),
        session: sqm.Session = fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    """Endpoint for booking a shipment.

    Args:
        manager_id (int): The manager's id.
        pfcom (ELClient, optional): The shipper object - defaults to fastapi.Depends(amherst.am_db.get_pfc).
        session (sqm.Session, optional): The database session - defaults to fastapi.Depends(amherst.am_db.get_session).

    Returns:
        - :meth:`~amherst.front.booked.booked_page`: Post-Booking Page on success.
        - :meth:`~amherst.front.ship.shipping_page`: Shipping Page on failure, which may include alerts.

    """
    logger.warning(f'booking_id: {manager_id}')
    man_in = await support.get_manager(manager_id, session)

    if man_in.shipment.booking_state is not None:
        logger.error(f'booking {manager_id} already booked')
        alert_dict = {'ALREADY BOOKED': 'ERROR'}
        return await booked.booked_page(manager=man_in, alert_dict=alert_dict)

    try:
        if man_in.shipment.direction == 'in':
            tod = dt.date.today()
            if man_in.shipment.ship_date <= tod:
                raise ValueError('CAN NOT COLLECT TODAY')

        req, resp = await book_shipment(man_in, pfcom)
        processed_manager = await process_shipment(man_in, pfcom, req, resp)
        if man_in.record.cmc_table_name == 'Hire':
            record_tracking(man_in)

        session.add(processed_manager)
        session.commit()
        man_out = ShipmentRecordOut.model_validate(processed_manager)
        return await booked.booked_page(manager=man_out)

    except Exception as err:
        alert_dict = {str(err): 'ERROR'}
        man_out = ShipmentRecordOut.model_validate(man_in)

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
        man_in.shipment.model_dump(exclude={'candidates'}),
        with_keys='YES'
    )
    return [c.Div(
        components=builders.list_of_divs(class_name='row my-2 mx-auto', components=texts),
        class_name='row'
    )]


async def book_shipment(manager: ShipmentRecordInDB, pfcom: ELClient):
    """Book a shipment.

    Args:
        manager (shipment_record.ShipmentRecordDB): The :class:`~managers.MANAGER_IN_DB` object.
        pfcom (ELClient): :class:`~ELClient` object.

    Returns:
        tuple: The request and response objects.

    """
    req = pfcom.state_to_request(manager.shipment)
    logger.warning(f'BOOKING ({manager.shipment.direction.title()}) {manager.record.name}')
    resp = pfcom.send_shipment_request(req)
    return req, resp


async def process_shipment(manager: ShipmentRecordDB, pfcom: ELClient, req, resp):
    """Process the shipment.

    Update the manager with the booking state and wait for the label to download.
    Open the label file in OS default pdf handler.

    Args:
        manager (shipment_record.ShipmentRecordDB): The manager object.
        pfcom (ELClient): :class:`~ELClient` object.
        req: The request object.
        resp: The response object.

    Returns:
        managers.ShipmentRecordDB: The manager object.

    Raises:
        shipaw.ExpressLinkError: If the shipment is not completed.

    """
    booked_state = ship_states.BookingState.model_validate(dict(request=req, response=resp))
    if alt := booked_state.alerts:
        raise shipaw.ExpressLinkError(str(alt))
        # if not resp.completed_shipment_info:
        # raise shipaw.ExpressLinkError(str(ship_states.response_alert_dict(resp)))

    new_ship_state = manager.shipment.model_copy(update={'booking_state': booked_state})
    val_ship_state = shipaw.Shipment.model_validate(new_ship_state)
    await support.wait_label(val_ship_state, pfcom)
    os.startfile(val_ship_state.booking_state.label_dl_path)
    manager.shipment = val_ship_state
    return manager


async def back_div(manager_id: int):
    """Back button."""
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                class_name='row btn btn-lg btn-primary',
                text='Back',
                on_click=events.GoToEvent(url=f'/ship/select/{manager_id}'),
            )
        ],
    )


async def confirm_div(manager):
    """Confirm button."""
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                text='Confirm Booking',
                on_click=e.GoToEvent(url=f'/book/go_book/{manager.id}'),
                class_name='row btn btn-lg btn-primary',
            )
        ],
    )

# unused?
# @router.post('/confirm_post/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
# async def confirm_post(
#         manager_id: int,
#         form: _t.Annotated[
#             ship_states.ShipStatePartial, fastui_form(ship_states.ShipStatePartial)],
#         pfcom: ELClient = fastapi.Depends(am_db.get_el_client),
#         session=fastapi.Depends(am_db.get_session),
#
# ):
#     """Endpoint for posting confirmation form."""
#     update = ship_states.ShipStatePartial.model_validate(form.model_dump())
#     if update.address.postcode:
#         update.candidates = pfcom.get_candidates(update.address.postcode)
#     await support.update_and_commit(manager_id, update, session)
#     return responses.RedirectResponse(url=f'/ship/select/{manager_id}')
