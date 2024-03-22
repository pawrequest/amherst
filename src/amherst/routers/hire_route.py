# from __future__ import annotations
import os

import fastapi
from fastapi import APIRouter, Depends
from fastui import FastUI, components as c, events
from loguru import logger
from sqlmodel import Session

import amherst.front.pages.shipping_page
import shipr
from amherst import am_db
from amherst.am_db import get_pfc, get_session
from amherst.front.pages import shipping_page
from amherst.models import am_shared, managers
from amherst.routers.booking_route import get_manager
from amherst.shipper import AmShipper
from pawdantic.pawui import builders
from shipr.ship_ui import states

router = APIRouter()


@router.get('/check_state/{man_id}', response_model=FastUI, response_model_exclude_none=True)
async def check_state(
        man_id: int,
        session=fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    man_in = await get_manager(man_id, session)
    texts = builders.dict_strs_texts(man_in.state.model_dump(), with_keys='YES')
    return [c.Div(
        components=builders.list_of_divs(
            components=texts
        ),
        class_name='row'
    )]


# @router.get('/open_hire_sheet/{manager_id}')
# async def open_hire_sheet(
#         manager_id: int,
#         session: Session = Depends(get_session),
# ):
#     man_in = await get_manager(manager_id, session)
#     hire_sheet = man_in.hire.record.get()


@router.get('/invoice/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def open_invoice(
        manager_id: int,
        session: Session = Depends(get_session),
) -> list[c.AnyComponent]:
    man_in = await get_manager(manager_id, session)
    man_out = managers.BookingManagerOut.model_validate(man_in)
    inv_file = man_in.item.record.get(am_shared.HireFields.INVOICE)

    try:
        os.startfile(inv_file)
    except (FileNotFoundError, TypeError):
        logger.error(f'Invoice file not found: {inv_file}')
        return await shipping_page.ship_page(
            manager=man_out,
            alert_dict={'INVOICE NOT FOUND': 'WARNING'}
        )
        # alert = pf_shared.Alert(code=11, message=f'Invoice file not found: {inv_file}', type='ERROR')

    return [c.FireEvent(event=events.GoToEvent(url=f'/hire/view/{manager_id}'))]

    # return await builders.page_w_alerts(
    #     components=[`
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

    # return c.FireEvent(event=events.GoToEvent(url=f'/book/view/{manager_id}'))


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
    return await amherst.front.pages.shipping_page.address_chooser(
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

    # updated_state_ = man_out.state.get_updated(updt)
    updated_state_ = man_in.state.get_updated(updt)
    updated_state = shipr.ShipState.model_validate(updated_state_)
    man_in.state = updated_state
    # man_out = managers.BookingManagerDB.model_validate(man_in)
    session.add(man_in)
    session.commit()
    session.refresh(man_in)
    man_out = managers.BookingManagerOut.model_validate(man_in)
    return await shipping_page.ship_page(manager=man_out)

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
    return await shipping_page.ship_page(manager=man_out)

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


# def hire_record_to_session(record: dict, session: sqm.Session, pfcom) -> managers.BookingManagerDB:
#     """Create a new hire and state in the database from a record dict."""
#     hire_ = hire_model.Hire(record=record)
#     ship = hire_model.ShipableItem.model_validate(hire_)
#     state = shipr.ShipState.hire_initial(hire_, pfcom)
#     manager = managers.BookingManagerDB(item=ship, state=state)
#     manager = manager.model_validate(manager)
#     session.add(manager)
#     session.commit()
#     session.refresh(manager)
#     return manager
