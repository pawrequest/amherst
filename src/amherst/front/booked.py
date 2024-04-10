from __future__ import annotations

import os
import pathlib

import fastapi
import flaskwebgui
import pdf_tools
from fastui import FastUI, components as c, events as e
from loguru import logger

import shipr
from amherst import am_db
from amherst.front import email_templates, support
from amherst.models import managers
from pawdantic.pawui import builders
from shipr.ship_ui import states as ship_states
from suppawt.office_ps.ms.outlook_handler import OutlookHandler

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


@router.get('/email_label/{booking_id}', response_model=FastUI, response_model_exclude_none=True)
async def email_label(
        booking_id: int,
        pfcom=fastapi.Depends(am_db.get_pfc),
        session=fastapi.Depends(am_db.get_session)
):
    """Endpoint to email the label for a booking."""
    logger.warning(f'printing id: {booking_id}')
    man_in = await support.get_manager(booking_id, session)
    send_label(man_in.state)
    return await booked_page(manager=man_in)


@router.get('/email_invoice/{booking_id}', response_model=FastUI, response_model_exclude_none=True)
async def email_invoice(
        booking_id: int,
        session=fastapi.Depends(am_db.get_session)
):
    """Endpoint to email the invoice for a booking."""
    man_in = await support.get_manager(booking_id, session)
    await send_invoice(man_in)
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


def send_label(state: shipr.ShipState):
    """Send the label by email."""
    email = email_templates.return_label_email(state)
    handler = OutlookHandler()
    handler.send_email(email)


async def send_invoice(manager: managers.BookingManagerOut):
    """Send invoice by email."""
    email = await email_templates.invoice_email(manager)
    handler = OutlookHandler()
    handler.send_email(email)


def get_named_labelpath(state: shipr.ShipState):
    """Get a named path (for saving) for the label."""
    pdir = os.environ.get('PARCELFORCE_LABELS_DIR')
    stt = f'Parcelforce Collection Label for {state.contact.business_name} on {state.ship_date}'
    return pathlib.Path(pdir) / f'{stt}.pdf'


async def prnt_label(label_path: pathlib.Path) -> None:
    """Print the labels. Arrays A6 Labels 2 to a A4 page.
    Uses pdf_tools.array_pdf.convert_many to print the labels.

    Args:
        label_path: The path to the label.

    """

    if not label_path.exists():
        logger.error(f'label_path {label_path} does not exist')

    pdf_tools.array_pdf.convert_many(label_path, print_files=True)


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
