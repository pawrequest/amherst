from __future__ import annotations

from fastui import AnyComponent
from fastui.events import GoToEvent

from amherst.front import amui, ui_helpers
from amherst.front.pages.base_page import BasePage
from amherst.models.hire_booking import HireBookingOut
from shipr.models import pf_ext
from shipr.models.ui_states import states


class AddressPage(BasePage):
    booking: HireBookingOut
    candidates: list[pf_ext.AddressRecipient]

    async def get_page(self) -> list[AnyComponent]:
        return await ui_helpers.page_w_alerts(
            components=[
                amui.Row(
                    components=[
                        amui.Button(
                            text=can.address_line1,
                            on_click=GoToEvent(
                                url=f"/hire/update/{self.booking.id}/{states.update_get_partial64(states.ShipStatePartial, address=can)}",
                            ),
                        )
                        for can in self.candidates
                    ],
                ),
            ],
            title="addresses",
        )
