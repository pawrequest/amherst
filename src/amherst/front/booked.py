from __future__ import annotations

import fastapi
import flaskwebgui
from fastui import FastUI
from fastui import components as c
from fastui import events as e
from loguru import logger

from amherst import am_db
from amherst.front import generic_emailer as ge
from amherst.front import support
from amherst.front.support import prnt_label
from amherst.models import managers
from pawdantic.pawui import builders
from shipr.ship_ui import states as ship_states

router = fastapi.APIRouter()


async def booked_page(manager: managers.MANAGER_IN_DB, alert_dict=None) -> list[c.AnyComponent]:
    """Page for post-booking actions including printing and emailing labels.

    Args:
        manager: The manager object.
        alert_dict: Dictionary of alerts.

    Returns:
        FastUI.Page: The page with the post-booking actions.

    """
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
            await email_label_div(manager),
            await email_invoice_div(manager),
            await open_invoice_div(manager),
            await email_missing_div(manager),
            await close_div(),
        ],
        title='booking',
        alert_dict=alert_dict,
    )
    return ret


async def print_div(manager):
    """Html Div with button to print labels."""
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


async def email_label_div(manager: managers.MANAGER_IN_DB):
    """Html Div with button to email labels."""
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                text=f'Email Labels for {manager.state.contact.business_name} to {manager.state.contact.email_address}',
                on_click=e.GoToEvent(
                    url=f'/booked/email_label/{manager.id}',
                ),
                class_name='btn btn-lg btn-primary'
            )
        ]
    )


async def email_invoice_div(manager: managers.MANAGER_IN_DB):
    """Html Div with button to email labels."""
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                text=f'Email Invoice for {manager.state.contact.business_name} to {manager.state.contact.email_address}',
                on_click=e.GoToEvent(
                    url=f'/booked/email_invoice/{manager.id}',
                ),
                class_name='btn btn-lg btn-primary'
            )
        ]
    )


async def email_missing_div(manager: managers.MANAGER_IN_DB):
    """Html Div with button to email missing items."""
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                text=f'Email Missing Items for {manager.state.contact.business_name} to {manager.state.contact.email_address}',
                on_click=e.GoToEvent(
                    url=f'/booked/email_missing/{manager.id}',
                ),
                class_name='btn btn-lg btn-primary'
            )
        ]
    )


async def close_div():
    """Html Div with button to close the application."""
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                text='Close Application',
                on_click=e.GoToEvent(
                    url='/booked/close_app/',
                ),
                class_name='btn btn-lg btn-primary'
            )
        ]
    )


async def open_invoice_div(manager: managers.BookingManagerOut) -> c.Div:
    """Div for opening invoice.

    Args:
        manager: Booking Manager

    Returns:
        c.Div: Div with button to fire GoToEvent to invoice endpoint

    """
    return c.Div(
        class_name='row mx-auto my-3',
        components=[
            c.Button(
                text='Open Invoice',
                on_click=e.GoToEvent(
                    url=f'/ship/invoice/{manager.id}',
                ),

            )
        ],
    )


@router.get('/email_label/{booking_id}', response_model=FastUI, response_model_exclude_none=True)
async def email_label(
        booking_id: int,
        session=fastapi.Depends(am_db.get_session)
):
    """Endpoint to email the label for a booking."""
    logger.warning(f'printing id: {booking_id}')
    man_in = await support.get_manager(booking_id, session)
    ge.send_label(man_in.state)
    return await booked_page(manager=man_in)


@router.get('/email_invoice/{booking_id}', response_model=FastUI, response_model_exclude_none=True)
async def email_invoice(
        booking_id: int,
        session=fastapi.Depends(am_db.get_session)
):
    """Endpoint to email the invoice for a booking."""
    man_in = await support.get_manager(booking_id, session)
    await ge.send_invoice(man_in)
    return await booked_page(manager=man_in)


@router.get('/email_missing/{booking_id}', response_model=FastUI, response_model_exclude_none=True)
async def email_missing(
        booking_id: int,
        session=fastapi.Depends(am_db.get_session)
):
    """Endpoint to email the missing items for a booking
    """
    man_in = await support.get_manager(booking_id, session)
    await ge.send_missing(man_in)
    return await booked_page(manager=man_in)


@router.get('/close_app/', response_model=None, response_model_exclude_none=True)
async def close_app(
):
    """Endpoint to close the application."""
    flaskwebgui.close_application()


@router.get('/print/{booking_id}', response_model=FastUI, response_model_exclude_none=True)
async def print_label(
        booking_id: int,
        session=fastapi.Depends(am_db.get_session)
):
    """Endpoint to print the label for a booking."""
    logger.warning(f'printing id: {booking_id}')
    man_in = await support.get_manager(booking_id, session)
    if not man_in.state.booking_state.label_downloaded:
        raise ValueError('label not downloaded')
    await prnt_label(man_in.state.booking_state.label_dl_path)
    return await booked_page(manager=man_in)


async def generic_email_div(manager: managers.MANAGER_IN_DB):
    return c.Div(
        class_name='row my-3',
        components=[
            ge.get_email_form(manager)
        ]
    )
