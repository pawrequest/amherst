# from __future__ import annotations
import os

import sqlmodel as sqm
from fastapi import APIRouter, Depends
from loguru import logger
from sqlmodel import Session
import shipr
from fastuipr import FastUI, builders, components as c, events
from shipr.ship_ui import states

import amherst.front.pages.hire_shipping
from amherst.am_db import get_pfc, get_session
from amherst.front.pages import hire_shipping
from amherst.models import am_shared, hire_model, managers
from amherst.routers.booking_route import get_manager
from amherst.shipper import AmShipper

router = APIRouter()


# @router.get('/open_hire_sheet/{manager_id}')
# async def open_hire_sheet(
#         manager_id: int,
#         session: Session = Depends(get_session),
# ):
#     man_in = await get_manager(manager_id, session)
#     hire_sheet = man_in.hire.record.get()

@router.get('/invoice/{manager_id}')
async def open_invoice(
        manager_id: int,
        session: Session = Depends(get_session),
):
    man_in = await get_manager(manager_id, session)
    inv_file = man_in.item.record.get(am_shared.AmherstFields.INVOICE)

    try:
        os.startfile(inv_file)
    except FileNotFoundError:
        logger.error(f'Invoice file not found: {inv_file}')
        # alert = pf_shared.Alert(code=11, message=f'Invoice file not found: {inv_file}', type='ERROR')

    # return await builders.page_w_alerts(
    #     components=[
    #         c.Button(
    #             text='Back',
    #             # on_click=c.FireEvent(event=events.GoToEvent(url=f'/book/view/{manager_id}')),
    #             on_click=events.GoToEvent(
    #                 url=f'/hire/invoice/{manager_id}',
    #             ),
    #         )
    #     ],
    #     title='back',
    # )

    return c.FireEvent(event=events.GoToEvent(url=f'/book/view/{manager_id}'))


@router.get('/neighbours/{booking_id}', response_model=FastUI, response_model_exclude_none=True)
async def neighbours(
        booking_id: int,
        pfcom: AmShipper = Depends(get_pfc),
        session: Session = Depends(get_session),
):
    man_in = await get_manager(booking_id, session)
    man_out = managers.BookingManagerOut.model_validate(man_in)
    postcode = man_in.hire.input_address.postcode
    candidates = pfcom.get_candidates(postcode)
    return await amherst.front.pages.hire_shipping.address_chooser(
        manager=man_out,
        candidates=candidates
    )


@router.get(
    '/pcneighbours/{booking_id}/{postcode}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def pcneighbours(
        booking_id: int,
        postcode: str,
        pfcom: AmShipper = Depends(get_pfc),
        session: Session = Depends(get_session),
):
    man_in = await get_manager(booking_id, session)
    man_out = managers.BookingManagerOut.model_validate(man_in)
    candidates = pfcom.get_candidates(postcode)
    return await amherst.front.pages.hire_shipping.address_chooser(
        manager=man_out,
        candidates=candidates
    )


@router.get(
    '/update/{booking_id}/{update_64}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def update_hire(
        booking_id: int,
        update_64: str | None = None,
        session: Session = Depends(get_session),
) -> list[c.AnyComponent]:
    updt = states.ShipStatePartial.model_validate_64(update_64)

    man_in = await get_manager(booking_id, session)
    man_out = managers.BookingManagerOut.model_validate(man_in)

    updated_state_ = man_out.state.get_updated(updt)
    updated_state = shipr.ShipState.model_validate(updated_state_)
    man_in.state = updated_state
    # man_out = managers.BookingManagerDB.model_validate(man_in)
    session.add(man_in)
    session.commit()
    session.refresh(man_in)
    return await hire_shipping.hire_page(manager=man_in)

    # return [c.Text(text="Booking not found")]


@router.get('/view/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def view_hire(
        manager_id: int,
        session: Session = Depends(get_session),
) -> list[c.AnyComponent]:
    logger.info(f'hire route: {manager_id}')
    man_in = await get_manager(manager_id, session)
    man_out = managers.BookingManagerOut.model_validate(man_in)
    if not man_out:
        raise ValueError(f'manager id {manager_id} not found')
    return await hire_shipping.hire_page(manager=man_out)


# @router.get('/new/{hire_name}')
# async def hire_from_cmc_name_64(
#         hire_name: str,
#         session=Depends(get_session),
#         # cursor: Csr = Depends(get_hire_cursor),
#         pfcom: AmShipper = Depends(get_pfc),
# ):
#     hire_name = base64.urlsafe_b64decode(hire_name).decode()
#     logger.info(f'hire_name: {hire_name}')
#     with pycommence.csr_context('Hire') as cursor:
#         hire_record = cursor.get_record(hire_name)
#
#     added = rec_importer.records_to_managers(hire_record, session=session, pfcom=pfcom)[0]
#
#     # hire = hire_record_to_session(hire_record, session, pfcom)
#     return [c.FireEvent(event=GoToEvent(url=f'/hire/view/{added.id}'))]


def hire_record_to_session(record: dict, session: sqm.Session, pfcom) -> managers.BookingManagerDB:
    """Create a new hire and state in the database from a record dict."""
    hire_ = hire_model.Hire(record=record)
    state = shipr.ShipState.hire_initial(hire_, pfcom)
    manager = managers.BookingManagerDB(hire=hire_, state=state)
    manager = manager.model_validate(manager)
    session.add(manager)
    session.commit()
    session.refresh(manager)
    return manager
