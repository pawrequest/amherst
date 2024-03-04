from __future__ import annotations

from amherst.models import hire_manager
from fastuipr import builders
from fastuipr import components as c
from fastuipr import events as e
from shipr.models.pf_shared import Alert


async def printed_page(manager: hire_manager.HireManager) -> list[c.AnyComponent]:
    ret = await builders.page_w_alerts(
        components=[
            c.Div.wrap(
                c.Button(
                    text='RePrint ',
                    # f"{self.booking.state.book_state.shipment_num()}"
                    # on_click=None,
                    on_click=e.GoToEvent(url=f'/book/print/{manager.id}'),
                ),
                c.Text(text='dddd'),
            ),
        ],
        title='Booking Response',
        alerts=await get_alerty(manager),
    )
    return ret


async def get_alerty(manager) -> list[Alert] | None:
    return manager.state.booking_state.response.alerts.alert if manager.state.booking_state else None


async def booked_page(manager: hire_manager.HireManager) -> list[c.AnyComponent]:
    ret = await builders.page_w_alerts(
        components=[
            c.Div.wrap(
                c.Button(
                    text=f'Download and Print Label for Shipment {manager.state.booking_state.shipment_num()}',
                    on_click=e.GoToEvent(
                        url=f'/book/print/{manager.id}',
                    ),
                ),
            ),
        ],
        title='booking',
        alerts=await get_alerty(manager),
    )
    return ret
