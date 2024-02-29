from __future__ import annotations

from fastui import AnyComponent, components as c
from fastui.events import GoToEvent

from amherst.front import amui
from amherst.front.pages.base_page import BasePage


class BookingPage(BasePage):
    state: BookedState

    async def get_page(self) -> list[AnyComponent]:
        ret = self.contained_page(
            amui.Row.wrap(
                amui.Button(
                    text=f"Download and Print Label for Shipment {self.state.shipment_num()}",
                    on_click=GoToEvent(url=f"/book/print/{self.state.model_dump_json()}"),
                ),
            ),
            title="booking",
        )

        return ret


def get_alerts(state: BookedState) -> list[c.AnyComponent]:
    alerts = [amui.Text(text=al.message) for al in state.alerts if hasattr(self.state, "response")]
    ret = amui.Page.default_page(*((*alerts,) if alerts else ()), *components, contained=True)
    return ret
    # *(alerts if alerts else ()),
    # amui.Row.wrap(*self.alert_texts),

    # @property
    # def shipment_number(self):
    #     return self.state.response.completed_shipment_info.completed_shipments.completed_shipment[0].shipment_number
