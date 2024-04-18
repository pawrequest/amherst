"""Pages and Enpoints for Post-Booking Actions."""
from __future__ import annotations

import fastapi
from fastui import FastUI, components as c, events as e
from loguru import logger

from amherst import am_db
from amherst.front import support
from amherst.front import shared
from amherst.front.support import get_manager_label_path, prnt_label_arrayed
from amherst.models import managers
from pawdantic.pawui import builders
from shipaw.ship_ui import states as ship_states

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
            await shared.invoice_div(manager),
            await shared.email_div(manager, ['invoice', 'label']),
            await shared.close_div(),
        ],
        title='Shipment Booked',
        alert_dict=alert_dict,
    )
    return ret


async def print_div(manager):
    """Html Div with button to print labels."""
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                text=rf'Array and Re/Print Labels for {manager.item.name}',
                on_click=e.GoToEvent(
                    url=f'/booked/print/{manager.id}',
                ),
                class_name='btn btn-lg btn-primary'
            )
        ]
    )


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
    await prnt_label_arrayed(await get_manager_label_path(man_in))
    return await booked_page(manager=man_in)
