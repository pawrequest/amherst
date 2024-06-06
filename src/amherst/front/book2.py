"""
Pages and Endpoints for Booking Shipments.
"""
from __future__ import annotations

import datetime as dt
import os

import fastapi
import sqlmodel as sqm
from comtypes import CoInitialize, CoUninitialize
from fastui import FastUI, components as c, events, events as e
from fastui.components.display import DisplayLookup, DisplayMode
from loguru import logger
from pawdantic.pawui import builders, pawui_types

import shipaw
from pycommence import PyCommence
from shipaw import BookingState, ELClient
from shipaw.ship_ui import states as ship_states
from shipaw.ship_ui.states import BookingState
from amherst import am_db
from amherst.front import booked2, ship, support
from amherst.front.support import get_shiprec
from amherst.models.shipment_record import (
    ShipmentRecordDB,
    ShipmentRecordInDB,
    ShipmentRecordOut,
    ShipmentRecord,
)

router = fastapi.APIRouter()


@router.get(
    '/confirm/{shiprec_id}/{shipment_64}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def confirm_or_back(
        shiprec_id: int,
        shipment_64: str,
        el_client: ELClient = fastapi.Depends(am_db.get_el_client),
        session: sqm.Session = fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    """Endpoint to submit shipment and return 'Confirm or Back' page.

    Args:
        shiprec_id (int): BookingManager id.
        shipment_64 (str): State as Base64 encoded JSON.
        el_client (ELClient, optional): The shipper object - defaults to fastapi.Depends(amherst.am_db.get_pfc).
        session (sqm.Session, optional): The database session - defaults to fastapi.Depends(amherst.am_db.get_session).

    Returns:
        c.Page: :meth:`~confirm_book_page`

    """
    shiprec = await get_shiprec(shiprec_id, session)

    shipment = ship_states.Shipment.model_validate_64(shipment_64)
    shipment.candidates = el_client.get_candidates(shipment.address.postcode)
    shiprec.shipment = shipaw.Shipment.model_validate(shipment)

    request = el_client.shipment_to_request(shipment)
    shiprec.booking_state = BookingState(request=request)
    # shiprec.model_validate(shiprec)

    session.add(shiprec)
    session.commit()
    # session.refresh(shiprec)
    # shiprec = await update_shiprec_shipment(shiprec_id, session, shipment)
    return await confirm_or_back_page(shiprec)


async def confirm_or_back_page(
        shiprec: ShipmentRecordDB, alert_dict: pawui_types.AlertDict = None
) -> list[c.AnyComponent]:
    """Confirm or Back page.

    Display the current shipment and buttons to proceed with booking or go back.

    Args:
        shiprec (managers.MANAGER_IN_DB): The shiprec object.
        alert_dict (pawui_types.AlertDict, optional): The alert dictionary - defaults to None.

    Returns:
        c.Page: Pre-Confirmation page.

    """

    return await builders.page_w_alerts(
        components=[
            c.Heading(
                text=f'Confirm details for {shiprec.record.name}',
                level=1,
                class_name='row mx-auto my-5'
            ),

            await confirm_div(shiprec),
            await back_div(shiprec.id),
            await simple_check(shiprec),
        ],
        title='booking',
        alert_dict=alert_dict,
    )


async def simple_check(shiprec):
    return c.Details(
        data=shiprec.booking_state,
        fields=[DisplayLookup(field='request', mode=DisplayMode.json)]
    )


@router.get('/go_book/{shiprec_id}', response_model=FastUI, response_model_exclude_none=True)
async def do_booking(
        shiprec_id: int,
        el_client: ELClient = fastapi.Depends(am_db.get_el_client),
        session: sqm.Session = fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    CoInitialize()

    logger.warning(f'booking_id: {shiprec_id}')
    shiprec = await support.get_shiprec(shiprec_id, session)

    if shiprec.booking_state.booked or shiprec.booking_state.completed:
        logger.error(f'Shipment for {shiprec.record.name} already booked')
        alert_dict = {'ALREADY BOOKED': 'ERROR'}
        return await booked2.booked_page(shiprec=shiprec, alert_dict=alert_dict)

    try:
        if shiprec.shipment.direction == 'in':
            tod = dt.date.today()
            if shiprec.shipment.ship_date <= tod:
                raise ValueError('CAN NOT COLLECT TODAY')

        processed_shiprec = await process_shipment_request(shiprec, el_client)
        session.add(processed_shiprec)
        session.commit()
        man_out = ShipmentRecordOut.model_validate(processed_shiprec)
        return await booked2.booked_page(shiprec=man_out)

    except Exception as err:
        alert_dict = {str(err): 'ERROR'}
        man_out = ShipmentRecordOut.model_validate(shiprec)

        return await ship.shipping_page(man_out.id, session=session, alert_dict=alert_dict)
    finally:
        CoUninitialize()


# async def book_shipment(shiprec: ShipmentRecordInDB, el_client: ELClient):
#     """Book a shipment.
#
#     Args:
#         shiprec (shipment_record.ShipmentRecordDB): The :class:`~managers.MANAGER_IN_DB` object.
#         el_client (ELClient): :class:`~ELClient` object.
#
#     Returns:
#         tuple: The request and response objects.
#
#     """
#     req = el_client.shipment_to_request(shiprec.shipment)
#     logger.warning(f'BOOKING ({shiprec.shipment.direction.title()}) {shiprec.record.name}')
#     resp = el_client.send_shipment_request(req)
#     return req, resp


# noinspection DuplicatedCode
async def process_shipment_request(shiprec: ShipmentRecordDB, el_client: ELClient):
    """Process the shipment.

    Update the shiprec with the booking shipment and wait for the label to download.
    Open the label file in OS default pdf handler.

    Args:
        shiprec (shipment_record.ShipmentRecordDB): The shiprec object.
        el_client (ELClient): :class:`~ELClient` object.
        req: The request object.

    Returns:
        managers.ShipmentRecordDB: The shiprec object.

    Raises:
        shipaw.ExpressLinkError: If the shipment is not completed.

    """
    req = shiprec.booking_state.request
    resp = el_client.send_shipment_request(req)
    booked_state = ship_states.BookingState.model_validate(dict(request=req, response=resp))
    shiprec.booking_state = booked_state

    if alt := booked_state.alerts:
        raise shipaw.ExpressLinkError(str(alt))

    label_path = shiprec.shipment.named_label_path
    await support.wait_label_decon(
        shipment_num=resp.shipment_num,
        dl_path=label_path,
        el_client=el_client
    )
    os.startfile(label_path)
    shiprec.booking_state.label_downloaded = True
    shiprec.booking_state.label_dl_path = label_path
    return shiprec


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
    return c.Div(class_name='row my-3', components=[c.Button(
            text='Confirm Booking',
            on_click=e.GoToEvent(url=f'/book/go_book/{manager.id}'),
            class_name='row btn btn-lg btn-primary',
        )])



# unused?
# @router.post('/confirm_post/{shiprec_id}', response_model=FastUI, response_model_exclude_none=True)
# async def confirm_post(
#         shiprec_id: int,
#         form: _t.Annotated[
#             ship_states.ShipmentPartial, fastui_form(ship_states.ShipmentPartial)],
#         el_client: ELClient = fastapi.Depends(am_db.get_el_client),
#         session=fastapi.Depends(am_db.get_session),
#
# ):
#     """Endpoint for posting confirmation form."""
#     update = ship_states.ShipmentPartial.model_validate(form.model_dump())
#     if update.address.postcode:
#         update.candidates = el_client.get_candidates(update.address.postcode)
#     await support.update_and_commit(shiprec_id, update, session)
#     return responses.RedirectResponse(url=f'/ship/select/{shiprec_id}')


def record_tracking(man_in: ShipmentRecordInDB):
    CoInitialize()

    try:
        tracking_number = man_in.shipment.booking_state.response.shipment_num
        category = man_in.record.cmc_table_name
        if category == 'Customer':
            logger.error('CANT LOG TO CUSTOMER')
            return
        record_name = man_in.record.name
        direction = man_in.shipment.direction
        do_record_tracking(category, direction, record_name, tracking_number)

    except Exception as exce:
        logger.error(f'Failed to record tracking for {man_in.record.name} due to:\n{exce}')

    finally:
        CoUninitialize()


def do_record_tracking(category, direction, record_name, tracking_number):
    py_cmc = PyCommence.from_table_name(table_name=category)
    tracking_link_field = 'Track Inbound' if direction == 'in' else 'Track Outbound'
    pf_url = 'https://www.parcelforce.com/track-trace?trackNumber='
    tracking_link = pf_url + tracking_number
    py_cmc.edit_record(
        record_name,
        {tracking_link_field: tracking_link, 'DB label printed': True}
    )
    logger.info(
        f'Updated "{record_name}" {tracking_link_field} to {tracking_link}'
    )
