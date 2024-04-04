from __future__ import annotations

from fastui import components as c, events, events as e

from amherst.models import managers
from pawdantic.pawui import builders, pawui_types
from shipr.ship_ui import states as ship_states


async def get_alerty(manager) -> pawui_types.AlertDict | None:
    if manager.state.booking_state:
        if alerts := manager.state.booking_state.state_alerts():
            return {a.message: a.type for a in alerts.alert}


async def confirm_book_page(
        manager: managers.MANAGER_IN_DB,
        alert_dict: pawui_types.AlertDict = None
) -> list[
    c.AnyComponent]:
    ret = await builders.page_w_alerts(
        # page_class_name='container-fluid',
        components=[
            c.Heading(
                text=f'Booking Confirmation for {manager.item.name}',
                level=1,
                class_name='row mx-auto my-5'
            ),
            c.ServerLoad(path=f'/sl/check_state/{manager.id}'),
            await confirm_div(manager),
            await back_div(),
        ],
        title='booking',
        alert_dict=alert_dict,
    )
    return ret


async def back_div():
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                class_name='row btn btn-lg btn-primary',
                text='Back',
                on_click=events.GoToEvent(url='/sp2/select/1'),
            )
        ]
    )


async def confirm_div(manager):
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                text='Confirm Booking',
                on_click=e.GoToEvent(url=f'/book/go_book/{manager.id}'),
                class_name='row btn btn-lg btn-primary'
            )
        ]
    )


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
                    url=f'/book/print/{manager.id}',
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
                    url=f'/book/email/{manager.id}',
                ),
                class_name='btn btn-lg btn-primary'
            )
        ]
    )
