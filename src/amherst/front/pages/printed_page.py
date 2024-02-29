from __future__ import annotations

from fastui import AnyComponent, components as c
from amherst.front import amui
from amherst.front.pages.base_page import BasePage
from shipr.models.booked_state import BookedState
from pawsupport.fastui_ps import Containable


class PrintedPage(BasePage):
    state: BookedState

    async def get_page(self) -> list[AnyComponent]:
        ret = self.contained_page(
            amui.Row.wrap(
                amui.Button(
                    text=f"RePrint {self.shipment_number}",
                    on_click=None,
                    # on_click=GoToEvent(url=f"/book/print/{self.shipment_number}"),
                ),
                amui.Text(text="dddd"),
            ),
            title="Booking Response",
        )
        return ret

    def contained_page(self, *components: Containable, **kwargs) -> list[c.AnyComponent]:
        alerts = [amui.Text(text=al.message) for al in self.alerts if hasattr(self.state, "response")]
        ret = amui.Page.default_page(*((*alerts,) if alerts else ()), *components, contained=True)
        return ret
        # *(alerts if alerts else ()),
        # amui.Row.wrap(*self.alert_texts),
