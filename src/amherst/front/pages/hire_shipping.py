from __future__ import annotations

import datetime as dt
import typing as _t

import pydantic as _p
from fastui import AnyComponent, components as c, events as e

from fastuipr import builders
from shipr.models import pf_ext, pf_shared
from shipr.ship_ui import states
import amherst.routers.forms
from amherst.front import amui, styles
from amherst.models import managers
from amherst.routers.forms import PostcodeSelect, VALID_PC


async def hire_page(
        manager: managers.BookingManager,
) -> list[
    c.AnyComponent]:
    return await builders.page_w_alerts(
        alert_dict=manager.state.alert_dict,
        components=[
            await main_row(manager),
            # await controls_row(manager),
        ],
    )

    # await self.service_button(),


async def main_row(manager: managers.BookingManager) -> c.Div:
    return builders.wrap_divs(
        components=[
            await left_col(manager),
            await middle_col(manager),
            await right_col(manager),
        ],
        class_name=styles.ROW_STYLE,
    )


async def left_col(manager) -> c.Div:
    return builders.wrap_divs(
        components=[
            await input_address_div(manager),
            await boxes_modal_row(manager),
            await date_modal_row(manager),
            *await book_modal(manager.id),
            # await open_invoice(manager),
        ],
        class_name=styles.LEFT_COL_STYLE,
    )


async def input_address_div(manager):
    con_txts = builders.object_strs_texts(manager.item.contact, title='Contact')
    add_txts = builders.object_strs_texts(manager.item.input_address, title='Address')
    con_rows = builders.list_of_divs(components=con_txts, class_name=styles.ROW_STYLE)
    add_rows = builders.list_of_divs(components=add_txts, class_name=styles.ROW_STYLE)
    return builders.wrap_divs(
        components=con_rows + add_rows,
        class_name=styles.COL_STYLE,
        inner_class_name=styles.ROW_STYLE,
    )


async def address_chooser_div(manager) -> c.Div:
    return builders.wrap_divs(
        components=[
            await choose_address_from_postcode(manager.id, manager.state.address.postcode),
        ],
        class_name=styles.ADDRESS_FROM_PC_STYLE,
    )


async def middle_col(manager):
    return builders.wrap_divs(
        components=[
            c.ModelForm(
                model=amherst.routers.forms.ContactForm.with_default(manager.state.contact),
                submit_url=f'/api/forms/contact/{manager.id}',
                submit_on_change=True,
            ),
            await address_chooser_div(manager),
        ],
        class_name=styles.COL_STYLE,
    )


async def right_col(manager):
    return builders.wrap_divs(
        components=[
            c.ModelForm(
                model=amherst.routers.forms.AddressForm.with_default(manager.state.address),
                submit_url=f'/api/forms/address/{manager.id}',
            ),
        ],
        class_name=styles.COL_STYLE,
    )


async def choose_address_from_postcode(man_id: int, postcode: str):
    return builders.wrap_divs(
        components=[
            c.ModelForm(
                model=PostcodeSelect.with_default(postcode),
                submit_url=f'/api/forms/postcode/{man_id}',
            ),
        ],
        class_name=styles.BOXES_BUTTON,
    )


async def neighbouring_addresses(man_id) -> c.Button:
    return c.Button(
        text='Choose neighbouring address',
        on_click=e.GoToEvent(
            url=f'/hire/neighbours/{man_id}',
        ),
    )


async def open_invoice(manager: managers.BookingManager) -> c.Button:
    return c.Button(
        text='Open Invoice',
        on_click=e.GoToEvent(
            url=f'/hire/invoice/{manager.id}',
        ),
    )


async def boxes_modal_row(manager: managers.BookingManager) -> c.Div:
    async def boxes_chooser_buttons() -> list[c.AnyComponent]:
        return [
            c.Button(
                text=str(i),
                on_click=e.GoToEvent(
                    url=f'/hire/update/{manager.id}/{manager.state.update_dump_64(boxes=i)}',
                ),
                class_name=styles.BOXES_BUTTON,
            )
            for i in range(1, 11)
        ]

    return builders.wrap_divs(
        components=[
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
        ],
        class_name=styles.ROW_STYLE,
    )


async def date_button(self):
    ...


async def service_button(self):
    ...


def default_pc(postcode):
    return _t.Annotated[VALID_PC, _p.Field(default=postcode)]


async def address_chooser(
        manager: managers.BookingManager, candidates: list[pf_ext.AddressRecipient]
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


async def date_modal_row(manager: managers.BookingManagerOut) -> c.Div:
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
                class_name=styles.BOXES_BUTTON,
            )
            for ship_date in weekday_dates
        ]

    return builders.wrap_divs(
        components=[
            c.Button(
                text=amui.date_string(manager.state.ship_date),
                on_click=e.PageEvent(
                    name='date-chooser',
                ),
                class_name=styles.BOXES_BUTTON,
            ),
            c.Modal(
                title='Date',
                body=await date_chooser_buttons(),
                footer=[
                    c.Button(text='Close', on_click=e.PageEvent(name='date-chooser', clear=True)),
                ],
                open_trigger=e.PageEvent(name='date-chooser'),
            ),
        ],
        class_name=styles.ROW_STYLE,
    )


async def book_modal(man_id):
    return (
        c.Button(
            text='Ship',
            on_click=e.PageEvent(name='ship-chooser'),
            class_name=styles.BOXES_BUTTON
        ),
        c.Modal(
            title='Confirm Shipping',
            body=[
                c.Button(
                    text='BOOK',
                    on_click=e.GoToEvent(
                        url=f'/book/go/{man_id}',
                    ),
                    class_name=styles.BOXES_BUTTON,
                ),
            ],
            footer=[
                c.Button(text='Close', on_click=e.PageEvent(name='ship-chooser', clear=True)),
            ],
            open_trigger=e.PageEvent(name='ship-chooser'),
        ),
    )

#
# async def address_modal(manager: managers.BookingManagerOut):
#     async def from_server():
#         return [
#             c.Button(
#                 text='Choose new address',
#                 on_click=e.GoToEvent(
#                     url=f'/hire/new_address/{manager.id}',
#                 ),
#             )
#         ]
#         # return [amui.Row.empty()]
#
#     return c.Modal(
#         title='Address Modal',
#         body=await from_server(),
#         footer=[
#             c.Button(text='Close', on_click=e.PageEvent(name='address-chooser', clear=True)),
#         ],
#         open_trigger=e.PageEvent(name='address-chooser'),
#     )
#
