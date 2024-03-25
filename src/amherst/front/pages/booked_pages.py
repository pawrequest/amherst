from __future__ import annotations

from fastui import components as c, events as e

from amherst.models import managers
from pawdantic.pawui import builders, pawui_types
from shipr.ship_ui import states as ship_states


async def get_alerty(manager) -> pawui_types.AlertDict | None:
    if manager.state.booking_state:
        if alerts := manager.state.booking_state.state_alerts():
            return {a.message: a.type for a in alerts.alert}


async def booked_page(manager: managers.BookedManager, alert_dict=None) -> list[c.AnyComponent]:
    state_alert_dict = ship_states.state_alert_dict(manager.state.booking_state)
    alert_dict = state_alert_dict.update(alert_dict or {})

    ret = await builders.page_w_alerts(
        components=[
            # c.Div.wrap(
            await print_div(manager),
        ],
        title='booking',
        alert_dict=alert_dict,
    )
    return ret


async def print_div(manager):
    return c.Div(
        components=[
            c.Button(
                text=f'Array and Re/Print Labels for {manager.item.name}',
                on_click=e.GoToEvent(
                    url=f'/book/print/{manager.id}',
                ),
                class_name='btn btn-lg btn-primary'
            )
        ]
    )


async def email_div(manager):
    return c.Div(
        components=[
            c.Button(
                text=f'Email Labels for {manager.item.name}',
                on_click=e.GoToEvent(
                    url=f'/book/email/{manager.id}',
                ),
                class_name='btn btn-lg btn-primary'
            )
        ]
    )
