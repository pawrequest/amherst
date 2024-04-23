from __future__ import annotations

import os

import fastapi
import sqlmodel
from fastapi import Depends
from fastui import FastUI, components as c, events, events as e
from loguru import logger

from amherst import am_db, am_types
from amherst.front import emailer, support
from amherst.front.ship import shipping_page
from amherst.models import managers

router = fastapi.APIRouter()


@router.get('/invoice/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def open_invoice(
        manager_id: int,
        session: sqlmodel.Session = Depends(am_db.get_session),
) -> support.Fui_Page:
    """Endpoint for opening invoice.

    Opens invoice file for the shipable_item in the booking manager.

    Args:
        manager_id: Booking Manager ID
        session: sqlmodel session

    Returns:
        Redirects to Shipping page with alert if invoice not found.

    """
    man_in = await support.get_manager(manager_id, session)
    inv_file = await support.get_invoice_path(man_in.record)
    man_out = managers.ShipmentRecordOut.model_validate(man_in)

    try:
        os.startfile(inv_file)
    except (FileNotFoundError, TypeError):
        logger.error(f'Invoice file not found: {inv_file}')
        return await shipping_page.ship_page(
            manager=man_out,
            alert_dict={'INVOICE NOT FOUND': 'WARNING'}
        )

    return [c.FireEvent(event=events.GoToEvent(url=f'/ship/select/{manager_id}'))]


async def invoice_div(manager: managers.ShipmentRecordOut) -> c.Div:
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
                    url=f'/shared/invoice/{manager.id}',
                ),

            )
        ],
    )


async def email_div(manager: managers.MANAGER_IN_DB, choices: list[am_types.EmailChoices]):
    return c.Div(
        class_name='row my-3',
        components=[
            emailer.get_email_form(manager, choices)
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
                    url='/close_app/',
                ),
                class_name='btn btn-lg btn-primary'
            )
        ]
    )
