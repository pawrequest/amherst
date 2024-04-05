from __future__ import annotations

import os
import pathlib

import fastapi
import pdf_tools
import sqlmodel
from fastui import FastUI, components as c, events as e
from loguru import logger

import shipr
from amherst import am_db
from amherst.front import support
from amherst.models import managers
from pawdantic.pawui import builders
from shipr.ship_ui import states as ship_states
from suppawt.office_ps.email_handler import Email
from suppawt.office_ps.ms.outlook_handler import OutlookHandler

router = fastapi.APIRouter()


async def booked_page(manager: managers.MANAGER_IN_DB, alert_dict=None) -> list[c.AnyComponent]:
    state_alert_dict = ship_states.state_alert_dict(manager.state.booking_state)
    alert_dict = state_alert_dict.update(alert_dict or {})

    ret = await builders.page_w_alerts(
        components=[
            c.Heading(
                text=f'Post-Booking for {manager.item.name}',
                level=1,
                class_name='row mx-auto my-5'
            ),

            await print_div(manager),
            await email_div(manager),
        ],
        title='booking',
        alert_dict=alert_dict,
    )
    return ret


async def print_div(manager):
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                text=f'Array and Re/Print Labels for {manager.item.name}',
                on_click=e.GoToEvent(
                    url=f'/booked/print/{manager.id}',
                ),
                class_name='btn btn-lg btn-primary'
            )
        ]
    )


async def email_div(manager: managers.MANAGER_IN_DB):
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                text=f'Email Labels for {manager.state.contact.business_name} to {manager.state.contact.email_address}',
                on_click=e.GoToEvent(
                    url=f'/booked/email/{manager.id}',
                ),
                class_name='btn btn-lg btn-primary'
            )
        ]
    )


# @router.get('/check_state/{man_id}', response_model=FastUI, response_model_exclude_none=True)
# async def check_state(
#         man_id: int,
#         session=fastapi.Depends(am_db.get_session),
# ) -> list[c.AnyComponent]:
#     man_in = await back_funcs.get_manager(man_id, session)
#     texts = builders.dict_strs_texts(
#         man_in.state.model_dump(exclude={'candidates'}),
#         with_keys='YES'
#     )
#     return [
#         c.Div(
#             components=builders.list_of_divs(
#                 class_name='row my-2 mx-auto',
#                 components=texts
#             ),
#             class_name='row'
#         )
#     ]


@router.get('/view/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def view_booked(
        manager_id: int,
        session: sqlmodel.Session = fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    manager = await support.get_manager(manager_id, session)
    manager_ = managers.BookingManagerOut.model_validate(manager)
    return await booked_page(manager=manager_)
    # return await builders.page_w_alerts(
    #     components=[
    #         builders.back_link,
    #     ],
    # )


@router.get('/email/{booking_id}', response_model=FastUI, response_model_exclude_none=True)
async def email_label(
        booking_id: int,
        pfcom=fastapi.Depends(am_db.get_pfc),
        session=fastapi.Depends(am_db.get_session)
):
    logger.warning(f'printing id: {booking_id}')
    man_in = await support.get_manager(booking_id, session)
    send_label(man_in.state)
    return await booked_page(manager=man_in)


@router.get('/print/{booking_id}', response_model=FastUI, response_model_exclude_none=True)
async def print_label(
        booking_id: int,
        session=fastapi.Depends(am_db.get_session)
):
    logger.warning(f'printing id: {booking_id}')
    man_in = await support.get_manager(booking_id, session)
    if not man_in.state.booking_state.label_downloaded:
        raise ValueError('label not downloaded')
    await prnt_label(man_in.state.booking_state.label_dl_path)
    return await booked_page(manager=man_in)


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


async def prnt_label(label_path: pathlib.Path) -> None:
    if not label_path.exists():
        logger.error(f'label_path {label_path} does not exist')

    pdf_tools.array_pdf.convert_many(label_path, print_files=True)
