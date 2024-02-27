from __future__ import annotations, annotations

import datetime

from fastui.events import GoToEvent, PageEvent
from fastui import components as c

from pawsupport.fastui_ps import fui
from shipr.models.pf_types import AddressChoice
from . import amui, css
from .amui import address_col, date_string
from .controller_abc import UIBase


class HireUI(UIBase):

    async def get_page(self) -> list[c.AnyComponent]:
        date_ = self.state.ship_date
        text = await date_string(date_)
        num_b = self.state.boxes

        return amui.Page.default_page(
            fui.Container.wrap(
                amui.Row(
                    components=[
                        # input address
                        amui.Col.wrap(
                            fui.Text(text=self.state.contact.business_name),
                            *await address_col(self.state.input_address),
                            wrap_inner=amui.Row
                        ),

                        # address buttons
                        amui.Col.wrap(
                            fui.Text(text=f'Address score: {self.state.address_choice.score}'),
                            c.Button(text="Choose this address"),
                            c.Button(text="Enter address manually", on_click=None),
                            c.Button(
                                text='Choose a Different Address',
                                on_click=PageEvent(name='address-chooser')
                            ),
                            await self.address_modal(),
                            wrap_inner=amui.Row,
                        ),
                        # output address
                        await address_col(self.state.address_choice.address, wrap_in=amui.Col)
                    ]
                ),
                amui.Row.wrap(
                    c.Button(
                        text=text,
                        on_click=PageEvent(
                            name='date-chooser',
                        ),
                    ),
                    await self.date_modal(),
                    c.Button(
                        text=f'{num_b} Boxes',
                        on_click=PageEvent(name='boxes-chooser'),
                        class_name=css.BOXES_BTN
                    ),
                    await self.boxes_modal(),
                    c.Button(
                        text='Ship',
                        on_click=PageEvent(name='ship-chooser'),
                    ),
                    await self.ship_modal(),
                )
            ),
            title="Hire Shipping"
        )

    async def ship_modal(self):
        async def ship_buttons():
            return [c.Button(
                text="Request Shipping",
                on_click=GoToEvent(
                    url=f'/book/go/{self.state.model_dump_json()}',
                    # query={
                    #     'state': 'sdfgdf'
                    # }
                )
            )
            ]

        return c.Modal(
            title='ship Modal',
            body=await ship_buttons(),
            footer=[
                c.Button(
                    text='Close',
                    on_click=PageEvent(name='ship-chooser', clear=True)
                ),
            ],
            open_trigger=PageEvent(name='ship-chooser'),
        )

    async def address_modal(self):
        async def address_chooser_buttons():
            return [
                c.Button(
                    text=can.address_line1,
                    on_click=GoToEvent(
                        url=f'/hire/id/{self.state.hire_id}',
                        query={
                            'state': self.state.update(
                                address_choice=AddressChoice(
                                    address=can,
                                    score=100
                                )
                            ).model_dump_json()
                        }
                    )
                )
                for can in self.state.candidates
            ]

        return c.Modal(
            title='Address Modal',
            body=await address_chooser_buttons(),
            footer=[
                c.Button(
                    text='Close',
                    on_click=PageEvent(name='address-chooser', clear=True)
                ),
            ],
            open_trigger=PageEvent(name='address-chooser'),
        )

    async def date_modal(self):
        async def date_chooser_buttons() -> list[c.AnyComponent]:
            start_date = datetime.date.today()
            date_range = [start_date + datetime.timedelta(days=x) for x in
                          range(7)]
            weekday_dates = [d for d in date_range if d.weekday() < 5]  # 0-4 are weekdays

            return [c.Button(
                text=await date_string(ship_date),
                on_click=GoToEvent(
                    url=f'/hire/id/{self.state.hire_id}',
                    # url='/book/go2',
                    query={'state': self.state.update(ship_date=ship_date).model_dump_json()}
                )
            ) for ship_date in weekday_dates
            ]

        return c.Modal(
            title='Date',
            body=await date_chooser_buttons(),
            footer=[
                c.Button(text='Close', on_click=PageEvent(name='date-chooser', clear=True)),
            ],
            open_trigger=PageEvent(name='date-chooser'),
        )

    async def boxes_modal(self):
        async def boxes_chooser_buttons() -> list[c.AnyComponent]:
            return [c.Button(
                text=str(i),
                on_click=GoToEvent(
                    url=f'/hire/id/{self.state.hire_id}',
                    query={'state': self.state.update(boxes=i).model_dump_json()}
                )
            ) for i in range(1, 11)
            ]

        return c.Modal(
            title='Number of Boxes',
            body=await boxes_chooser_buttons(),
            footer=[
                c.Button(text='Close', on_click=PageEvent(name='boxes-chooser', clear=True)),
            ],
            open_trigger=PageEvent(name='boxes-chooser'),
            open_context={'oc': 'boxes'}
        )
