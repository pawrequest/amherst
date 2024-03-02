from __future__ import annotations

from fastui import AnyComponent
from fastui.events import GoToEvent

from amherst.front import amui, ui_helpers
from amherst.front.pages.base_page import BasePage
from amherst.models.hire_booking import HireBookingOut


class BookedPage(BasePage):
    booking: HireBookingOut

    async def get_page(self) -> list[AnyComponent]:
        ret = await ui_helpers.page_w_alerts(
            components=[
                amui.Row.wrap(
                    amui.Button(
                        text=f"Download and Print Label for Shipment {self.booking.state.shipment_num()}",
                        on_click=GoToEvent(
                            url="/print/label/",
                            # query={"state": 'eeee'},
                        ),
                    ),
                ),
            ],
            title="booking",
        )
        return ret


class PrintedPage(BasePage):
    booking: HireBookingOut

    async def get_page(self) -> list[AnyComponent]:
        ret = await ui_helpers.page_w_alerts(
            components=[
                amui.Row.wrap(
                    amui.Button(
                        text=f"RePrint "
                        # f"{self.booking.state.book_state.shipment_num()}"
                        ,
                        # on_click=None,
                        on_click=GoToEvent(url=f"/book/print/{self.booking.id}"),
                    ),
                    amui.Text(text="dddd"),
                ),
            ],
            title="Booking Response",
        )
        return ret
