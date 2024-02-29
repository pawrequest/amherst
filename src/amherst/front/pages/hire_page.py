from __future__ import annotations, annotations

import datetime

from fastui.events import GoToEvent, PageEvent
from fastui import components as c

from amherst.front.ui_helpers import page_w_alerts
from shipr.models.booking_state import BookingStateUpdater
from amherst.models.hire_state import HireState
from pawsupport.fastui_ps import fui
from amherst.front import amui, css
from amherst.front.pages.base_page import BasePage


class HirePage(BasePage):
    state: HireState

    async def get_page(self) -> list[c.AnyComponent]:
        date_ = self.state.ship_date
        text = await amui.date_string_as(date_)

        return await page_w_alerts(
            alerts=[],
            components=[
                # ADDRESS AND CONTROLS ROW
                amui.Row.wrap(
                    # INPUT ADDRESS
                    amui.Col.wrap(
                        fui.Text(text=self.state.contact.business_name),
                        *await amui.address_col(self.state.input_address),
                        wrap_inner=amui.Row,
                    ),
                    # BUTTONS
                    amui.Col.wrap(
                        c.Button(text="Choose this address"),
                        c.Button(text="Enter address manually", on_click=None),
                        c.Button(text="Choose a Different Address", on_click=PageEvent(name="address-chooser")),
                        await self.address_modal(),
                        wrap_inner=amui.Row,
                    ),
                    # CHOSEN ADDRESS
                    await amui.address_col(self.state.address, wrap_in=amui.Col),
                ),
                # DATE AND BOXES AND SHIP ROW
                amui.Row.wrap(
                    ## DATE MODAL BUTTON
                    c.Button(
                        text=text,
                        on_click=PageEvent(
                            name="date-chooser",
                        ),
                    ),
                    await self.date_modal(),
                    ## BOXES MODAL BUTTON
                    c.Button(
                        text=f"{self.state.boxes} Boxes",
                        on_click=PageEvent(name="boxes-chooser"),
                        class_name=css.BOXES_BTN,
                    ),
                    await self.boxes_modal(),
                    ## SHIP MODAL BUTTON
                    c.Button(text="Ship", on_click=PageEvent(name="ship-chooser"), class_name=css.BOXES_BTN),
                    await self.ship_modal(),
                    # c.Button(text="Ship2", on_click=PageEvent(name="ship-chooser2")),
                    # await self.ship_modal2(),
                ),
            ],
        )

    async def ship_modal(self):
        return c.Modal(
            title="ship Modal",
            body=[
                c.Button(
                    text="Request Shipping",
                    on_click=GoToEvent(
                        url="/book/go/",
                        query=self.state.update_query(),
                    ),
                )
            ],
            footer=[
                c.Button(text="Close", on_click=PageEvent(name="ship-chooser", clear=True)),
            ],
            open_trigger=PageEvent(name="ship-chooser"),
        )

    async def address_modal(self):
        async def from_server():
            # todo dubious circular?
            return [
                # c.ServerLoad(
                #     path=f"/sl/candidate_buttons/{self.state.hire.id}/{self.state.address.postcode}",
                #     load_trigger=PageEvent(name="address-chooser"),
                #     components=await candidate_buttons(
                #         hire_id=self.state.hire.id, postcode=self.state.address.postcode
                #     ),
                # )
            ]
            return [amui.Row.empty()]

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
                        url=f"/hire/update_/{self.state.hire.id}",
                        query=BookingStateUpdater(ship_date=ship_date).update_query(),
                    ),
                )
                for ship_date in weekday_dates
            ]

        return c.Modal(
            title="Date",
            body=await date_chooser_buttons(),
            footer=[
                c.Button(text="Close", on_click=PageEvent(name="date-chooser", clear=True)),
            ],
            open_trigger=PageEvent(name="date-chooser"),
        )

    async def boxes_modal(self):
        async def boxes_chooser_buttons() -> list[c.AnyComponent]:
            return [
                c.Button(
                    text=str(i),
                    on_click=GoToEvent(
                        url=f"/hire/update_/{self.state.hire.id}",
                        query=BookingStateUpdater(boxes=i).update_query(),
                        # query={"q": "query"},
                    ),
                )
                for i in range(1, 11)
            ]

        return c.Modal(
            title="Number of Boxes",
            body=await boxes_chooser_buttons(),
            footer=[
                c.Button(text="Close", on_click=PageEvent(name="boxes-chooser", clear=True)),
            ],
            open_trigger=PageEvent(name="boxes-chooser"),
        )
