from __future__ import annotations

import datetime as dt
import typing as _t

import pydantic as _p

import amherst.routers.forms
from amherst.front import amui
from amherst.models import hire_manager
from amherst.routers.forms import VALID_PC, PostcodeSelect
from fastui import AnyComponent, builders, styles
from fastui import components as c
from fastui import events as e
from fastui.types_ import ModalType
from shipr.models import pf_ext
from shipr.ship_ui import states


async def hire_page(manager: hire_manager.HireManager) -> list[c.AnyComponent]:
    return await builders.page_w_alerts(
        alerts=[],
        components=[
            await address_row(manager),
            await controls_row(manager),
        ],
    )

    # await self.service_button(),
    # await self.manual_entry(),


async def address_row(manager: hire_manager.HireManager) -> c.Div:
    return c.Div.wrap(
        await input_address_col(manager),
        await contact_form_col(manager),
        await address_form_col(manager),
        class_name=styles.ROW_STYLE,
    )


async def input_address_col(manager):
    return c.Div.wrap(
        await amui.address_n_contact_col(
            address=manager.hire.input_address, contact=manager.hire.contact, title_prefix='Input '
        ),
        await address_from_postcode_col(manager.id, manager.state.address.postcode),
        class_name=styles.COL_STYLE,
    )


async def contact_form_col(manager):
    return c.Div.wrap(
        c.ModelForm(
            model=amherst.routers.forms.ContactForm.with_default(manager.state.contact),
            submit_url=f'/api/forms/contact/{manager.id}',
        ),
        class_name=styles.COL_STYLE,
    )


async def address_form_col(manager):
    return c.Div.wrap(
        c.ModelForm(
            model=amherst.routers.forms.AddressForm.with_default(manager.state.address),
            submit_url=f'/api/forms/address/{manager.id}',
        ),
        class_name=styles.COL_STYLE,
    )


async def address_from_postcode_col(man_id: int, postcode: str):
    return c.Div.wrap(
        c.ModelForm(
            model=PostcodeSelect.with_default(postcode),
            submit_url=f'/api/forms/postcode/{man_id}',
        ),
        class_name=styles.ROW_STYLE,
    )


async def controls_row(manager):
    return c.Div.wrap(
        *await boxes_modal(manager),
        *await date_modal(manager),
        *await book_modal(manager.id),
        class_name=styles.ROW_STYLE,
        # inner_class_name=styles.COL_STYLE,
    )


async def neighbouring_addresses(man_id) -> c.Button:
    return c.Button(
        text='Choose neighbouring address',
        on_click=e.GoToEvent(
            url=f'/hire/neighbours/{man_id}',
        ),
    )


async def boxes_modal(manager: hire_manager.HireManager) -> ModalType:
    async def boxes_chooser_buttons() -> list[c.AnyComponent]:
        return [
            c.Button(
                text=str(i),
                on_click=e.GoToEvent(
                    url=f'/hire/update/{manager.id}/{manager.state.update_dump_64(boxes=i)}',
                ),
            )
            for i in range(1, 11)
        ]

    return (
        c.Button(
            text=f'{manager.state.boxes} Boxes',
            on_click=e.PageEvent(name='boxes-chooser'),
            class_name=styles.BOXES_BUTTON,
        ),
        c.Modal(
            title='Number of Boxes',
            body=await boxes_chooser_buttons(),
            footer=[
                c.Button(text='Close', on_click=e.PageEvent(name='boxes-chooser', clear=True)),
            ],
            open_trigger=e.PageEvent(name='boxes-chooser'),
        ),
    )


async def date_button(self):
    ...


async def service_button(self):
    ...


def default_pc(postcode):
    return _t.Annotated[VALID_PC, _p.Field(default=postcode)]


async def address_chooser(
    manager: hire_manager.HireManager, candidates: list[pf_ext.AddressRecipient]
) -> list[AnyComponent]:
    return await builders.page_w_alerts(
        components=[
            c.Div(
                components=[
                    c.Button(
                        text=can.address_line1,
                        on_click=e.GoToEvent(
                            url=f'/hire/update/{manager.id}/{manager.state.update_dump_64_o(states.ShipStatePartial(address=can))}',
                        ),
                    )
                    for can in candidates
                ],
            ),
        ],
        title='addresses',
    )


async def date_modal(manager: hire_manager.HireManagerOut) -> ModalType:
    async def date_chooser_buttons() -> list[c.AnyComponent]:
        start_date = dt.date.today()
        date_range = [start_date + dt.timedelta(days=x) for x in range(7)]
        weekday_dates = [d for d in date_range if d.weekday() < 5]  # 0-4 are weekdays

        return [
            c.Button(
                text=amui.date_string(ship_date),
                on_click=e.GoToEvent(
                    url=f'/hire/update/{manager.id}/{manager.state.update_dump_64_o(states.ShipStatePartial(ship_date=ship_date))}',
                ),
            )
            for ship_date in weekday_dates
        ]

    return (
        c.Button(
            text=amui.date_string(manager.state.ship_date),
            on_click=e.PageEvent(
                name='date-chooser',
            ),
        ),
        c.Modal(
            title='Date',
            body=await date_chooser_buttons(),
            footer=[
                c.Button(text='Close', on_click=e.PageEvent(name='date-chooser', clear=True)),
            ],
            open_trigger=e.PageEvent(name='date-chooser'),
        ),
    )


async def book_modal(man_id):
    return (
        c.Button(text='Ship', on_click=e.PageEvent(name='ship-chooser'), class_name=styles.BOXES_BUTTON),
        c.Modal(
            title='ship Modal',
            body=[
                c.Button(
                    text='BOOK',
                    on_click=e.GoToEvent(
                        url=f'/book/go/{man_id}',
                    ),
                ),
            ],
            footer=[
                c.Button(text='Close', on_click=e.PageEvent(name='ship-chooser', clear=True)),
            ],
            open_trigger=e.PageEvent(name='ship-chooser'),
        ),
    )


async def address_modal(manager: hire_manager.HireManagerOut):
    async def from_server():
        return [
            c.Button(
                text='Choose new address',
                on_click=e.GoToEvent(
                    url=f'/hire/new_address/{manager.id}',
                ),
            )
        ]
        # return [amui.Row.empty()]

    return c.Modal(
        title='Address Modal',
        body=await from_server(),
        footer=[
            c.Button(text='Close', on_click=e.PageEvent(name='address-chooser', clear=True)),
        ],
        open_trigger=e.PageEvent(name='address-chooser'),
    )


#
# async def candidate_frame(manager):
#     poc_select = PostcodeSelect(postcode=manager.hire.input_address.postcode)
#     return await builders.page_w_alerts(
#         components=[
#             c.Div.wrap(c.Text(text=f'{manager.hire.name}'), class_name=styles.ROW_STYLE),
#             *[
#                 c.Div(
#                     components=[
#                         c.Button(
#                             text=can.address_line1,
#                             on_click=e.GoToEvent(
#                                 url=f'/hire/update/{manager.id}/{manager.state.update_dump_64(address=can)}'
#                             ),
#                         )
#                         for can in candidates
#                     ]
#                 )
#             ],
#         ]
#     )
