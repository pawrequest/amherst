
from fastui import components as c

from amherst.front import amui
from amherst.front.controller_abc import UIBase


class BookingUI(UIBase):
    async def get_page(self) -> list[c.AnyComponent]:
        return amui.Page.default_page(
                c.Text(text="Booking UI")
        )
