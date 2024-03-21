from __future__ import annotations

from pawdantic.pawui import builders, types_ as f_types
from fastui import components as c, events as e

from amherst.models import managers


async def get_alerty(manager) -> f_types.AlertDict | None:
    if manager.state.booking_state:
        if alerts := manager.state.booking_state.response.alerts:
            return {a.message: a.type for a in alerts.alert}


async def booked_page(manager: managers.BookingManager) -> list[c.AnyComponent]:
    ret = await builders.page_w_alerts(
        components=[
            # c.Div.wrap(
            c.Button(
                text=f'Array and Re/Print Labels for {manager.item.name}',
                on_click=e.GoToEvent(
                    url=f'/book/print/{manager.id}',
                ),
                class_name='btn btn-lg btn-primary'
            ),
            # c.Button(
            #     text='Open Invoice',
            #     on_click=e.GoToEvent(
            #         url=f'/hire/invoice/{manager.id}',
            #     ),
            # ),
            # page_class_name=styles.CONTAINER_STYLE,
            # inner_class_name=styles.ROW_STYLE,
            # ),
        ],
        title='booking',
        alert_dict=await get_alerty(manager),
    )
    return ret
