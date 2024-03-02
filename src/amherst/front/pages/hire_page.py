from __future__ import annotations, annotations

import datetime

import pydantic
from fastui.events import GoToEvent, PageEvent
from fastui import components as c

from amherst.front import amui, css, ui_helpers
from amherst.models import hire_booking
from pawsupport.fastui_ps import fui
from amherst.front.pages.base_page import BasePage
from shipr.models.ui_states import states
from shipr.models.ui_states.states import update_get_partial64


class PostcodeSelect(pydantic.BaseModel):
    postcode: str


class HirePage(BasePage):
    booking: hire_booking.HireBooking

    def postcode_select(self):
        return c.ModelForm(model=PostcodeSelect, submit_url="/api/forms/postcode")

    async def get_page(self) -> list[c.AnyComponent]:
        return await ui_helpers.page_w_alerts(
            alerts=[],
            components=[
                # ADDRESS AND CONTROLS ROW
                amui.Row.wrap(
                    await self.in_add_col(),
                    await self.control_buttons(),
                    await amui.address_col(self.booking.state.address, wrap_in=amui.Col),
                ),
                amui.Row.wrap(
                    *await self.date_modal(),
                    *await self.boxes_modal(),
                    *await self.book_modal(),
                ),
            ],
        )

    async def control_buttons(self):
        return amui.Col.wrap(
            amui.Row.empty(),
            c.Button(text="Enter address manually", on_click=None),
            c.Button(
                text="Choose new address",
                on_click=GoToEvent(
                    url=f"/hire/new_address/{self.booking.id}",
                ),
            ),
            self.postcode_select(),
            wrap_inner=amui.Row,
        )

    async def in_add_col(self):
        return amui.Col.wrap(
            fui.Text(text=self.booking.hire.contact.business_name),
            *await amui.address_col(self.booking.hire.input_address),
            wrap_inner=amui.Row,
        )

    async def book_modal(self):
        return (c.Button(
            text="Ship",
            on_click=PageEvent(name="ship-chooser"),
            class_name=css.BOXES_BTN
        ),
                c.Modal(
                    title="ship Modal",
                    body=[
                        c.Button(
                            text='boopkj',
                            on_click=GoToEvent(
                                url=f"/book/go/{self.booking.id}",
                            ),
                        ),
                    ],
                    footer=[
                        c.Button(text="Close", on_click=PageEvent(name="ship-chooser", clear=True)),
                    ],
                    open_trigger=PageEvent(name="ship-chooser"),
                )
        )

    async def address_modal(self):
        async def from_server():
            return [
                c.Button(
                    text="Choose new address",
                    on_click=GoToEvent(
                        url=f"/hire/new_address/{self.booking.id}",
                    ),
                )
            ]
            # return [amui.Row.empty()]

        return c.Modal(
            title="Address Modal",
            body=await from_server(),
            footer=[
                c.Button(text="Close", on_click=PageEvent(name="address-chooser", clear=True)),
            ],
            open_trigger=PageEvent(name="address-chooser"),
        )

    async def date_modal(self):
        async def date_chooser_buttons() -> list[c.AnyComponent]:
            start_date = datetime.date.today()
            date_range = [start_date + datetime.timedelta(days=x) for x in range(7)]
            weekday_dates = [d for d in date_range if d.weekday() < 5]  # 0-4 are weekdays

            return [
                c.Button(
                    text=await amui.date_string_as(ship_date),
                    on_click=GoToEvent(
                        url=f"/hire/update/{self.booking.id}/{update_get_partial64(states.ShipStatePartial, ship_date=ship_date)}",
                        # query=self.booking.state.update_get_query64(
                        #     ship_date=ship_date
                        # ),
                    ),
                )
                for ship_date in weekday_dates
            ]

        return (c.Button(
            text=await amui.date_string_as(self.booking.state.ship_date),
            on_click=PageEvent(
                name="date-chooser",
            ),
        ),
                c.Modal(
                    title="Date",
                    body=await date_chooser_buttons(),
                    footer=[
                        c.Button(text="Close", on_click=PageEvent(name="date-chooser", clear=True)),
                    ],
                    open_trigger=PageEvent(name="date-chooser"),
                ))

    async def boxes_modal(self):
        async def boxes_chooser_buttons() -> list[c.AnyComponent]:
            return [
                c.Button(
                    text=str(i),
                    on_click=GoToEvent(
                        url=f"/hire/update/{self.booking.id}/{update_get_partial64(states.ShipStatePartial, boxes=i)}",
                    ),
                )
                for i in range(1, 11)
            ]

        return (c.Button(
            text=f"{self.booking.state.boxes} Boxes",
            on_click=PageEvent(name="boxes-chooser"),
            class_name=css.BOXES_BTN,
        ),
                c.Modal(
                    title="Number of Boxes",
                    body=await boxes_chooser_buttons(),
                    footer=[
                        c.Button(
                            text="Close",
                            on_click=PageEvent(name="boxes-chooser", clear=True)
                        ),
                    ],
                    open_trigger=PageEvent(name="boxes-chooser"),
                ))
