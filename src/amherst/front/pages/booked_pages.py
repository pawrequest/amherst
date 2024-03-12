from __future__ import annotations

from fastuipr import builders, components as c, events as e
from shipr.models.pf_shared import Alert

from amherst.models import managers


async def get_alerty(manager) -> list[Alert] | None:
    if manager.state.booking_state:
        if alerts := manager.state.booking_state.response.alerts:
            return alerts.alert
    return None


async def booked_page(manager: managers.BookingManager) -> list[c.AnyComponent]:
    ret = await builders.page_w_alerts(
        components=[
            # c.Div.wrap(
            c.Button(
                text=f'Array and Re/Print Labels for {manager.item.name}',
                on_click=e.GoToEvent(
                    url=f'/book/print/{manager.id}',
                ),
                class_name='btn btn-lg'
            ),
            # c.Button(
            #     text='Open Invoice',
            #     on_click=e.GoToEvent(
            #         url=f'/hire/invoice/{manager.id}',
            #     ),
            # ),
            # class_name=styles.CONTAINER_STYLE,
            # inner_class_name=styles.ROW_STYLE,
            # ),
        ],
        title='booking',
        alerts=await get_alerty(manager),
    )
    return ret
