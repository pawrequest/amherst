from __future__ import annotations

import datetime as dt
import typing as _t

from fastui import AnyComponent, components as c, events as e

import shipr.ship_ui.forms
from amherst.front import amui, styles as am_styles
from amherst.models import managers
from pawdantic.pawui import builders, styles
from shipr.models import pf_ext
from shipr.models.types import PostcodeSelect
from shipr.ship_ui import states


async def hire_page(
        manager: managers.BookingManagerOut,
) -> list[
    c.AnyComponent]:
    return await builders.page_w_alerts(
        alert_dict=manager.state.alert_dict,
        page_class_name=am_styles.PAGE_STYLE,
        container_class_name=am_styles.CONTAINER_STYLE,
        components=[await main_row(manager)],
    )

    # await self.service_button(),


async def main_row(manager: managers.BookingManagerOut) -> c.Div:
    return builders.wrap_divs(
        components=[
            await left_col(manager),
            await right_col(manager),
        ],
        class_name='row my-3',
    )


async def left_col(manager) -> c.Div:
    return c.Div(
        class_name='col col-4 mx-auto',
        components=[
            await input_address_div(manager),
            await boxes_modal_row(manager),
            await date_modal_div(manager),
            await open_invoice(manager),
            # await outbound_modal_div(manager),
            # await inbound_modal_div(manager),
            await booking_div(manager, 'in'),
            await booking_div(manager, 'out'),
            await address_chooser_div(manager),

            # await away_collection_row(manager.id),

        ],
    )


async def input_address_div(manager, class_name='row', inner_class_name='row') -> c.Div:
    return c.Div(
        class_name=class_name,
        components=[
            *builders.list_of_divs(
                class_name=inner_class_name,
                components=[
                    *builders.dict_strs_texts(manager.item.contact.model_dump(), title='Contact'),
                    *builders.dict_strs_texts(
                        manager.item.input_address.model_dump(),
                        title='Address'
                    ),
                ],
            ),
        ],
    )


async def address_chooser_div(manager) -> c.Div:
    return c.Div(
        components=[
            # await choose_address_from_postcode(manager.id, manager.state.address.postcode),
            c.Div(
                components=[
                    c.ModelForm(
                        model=PostcodeSelect.with_default(manager.state.address.postcode),
                        submit_url=f'/api/forms/postcode/{manager.id}',
                        class_name='row h6',
                    ),
                ],
                class_name=am_styles.BUTTON,
            )
        ],
        class_name='row mx-auto',
    )


async def middle_col(manager):
    return c.Div(
        components=[
            c.ModelForm(
                model=shipr.ship_ui.forms.ContactForm.with_default(manager.state.contact),
                submit_url=f'/api/forms/contact/{manager.id}',
                submit_on_change=True,
            ),
            await address_chooser_div(manager),
        ],
        class_name='col',
    )


async def right_col(manager):
    return c.Div(
        components=[
            c.ModelForm(
                # model=shipr.ship_ui.forms.AddressForm.with_default(manager.state.address),
                model=shipr.ship_ui.forms.ContactAndAddressForm.with_default(
                    manager.state.contact,
                    manager.state.address
                ),
                submit_url=f'/api/forms/address/{manager.id}',
                class_name='row h6',
                # submit_on_change=True,
            ),
        ],
        class_name='col',
    )


async def choose_address_from_postcode(man_id: int, postcode: str):
    return c.Div(
        components=[
            c.ModelForm(
                model=PostcodeSelect.with_default(postcode),
                submit_url=f'/api/forms/postcode/{man_id}',
            ),
        ],
        class_name=am_styles.BUTTON,
    )


async def open_invoice(manager: managers.BookingManagerOut) -> c.Div:
    return c.Div(
        components=[
            c.Button(
                text='Open Invoice',
                on_click=e.GoToEvent(
                    url=f'/hire/invoice/{manager.id}',
                ),
            )
        ],
        class_name=styles.ROW_STYLE,
    )


async def boxes_modal_row(manager: managers.BookingManagerOut) -> c.Div:
    async def boxes_chooser_button_rows() -> list[c.Div]:
        return builders.list_of_divs(
            class_name='row',
            components=[
                c.Button(
                    text=str(i),
                    on_click=e.GoToEvent(
                        url=f'/hire/update/{manager.id}/{manager.state.update_dump_64(boxes=i)}',
                    ),
                    class_name=am_styles.BUTTON,
                )
                for i in range(1, 11)
            ],
        )

    return c.Div(
        components=[
            c.Button(
                text=f'{manager.state.boxes} Boxes',
                on_click=e.PageEvent(name='boxes-chooser'),
                class_name=am_styles.BUTTON,
            ),
            c.Modal(
                title='Number of Boxes',
                body=await boxes_chooser_button_rows(),
                footer=[
                    c.Button(text='Close', on_click=e.PageEvent(name='boxes-chooser', clear=True)),
                ],
                open_trigger=e.PageEvent(name='boxes-chooser'),
            ),
        ],
        class_name=styles.ROW_STYLE,
    )


async def service_button(self):
    ...


async def address_chooser(
        manager: managers.BookingManagerOut, candidates: list[pf_ext.AddressRecipient]
) -> list[AnyComponent]:
    return await builders.page_w_alerts(
        alert_dict=manager.state.alert_dict,
        components=[
            c.Div(
                class_name='row my-2',
                components=[
                    c.Button(
                        text=can.address_line1,
                        on_click=e.GoToEvent(
                            url=f'/hire/update/{manager.id}/{manager.state.update_dump_64_o(states.ShipStatePartial(address=can))}',
                        ),
                    )
                ],
            )
            for can in candidates
        ],
        title='addresses',
    )


# async def address_chooser_modal_div(manager: managers.BookingManagerOut, class_name='row') -> c.Div:
#     async def address_chooser_buttons() -> list[c.AnyComponent]:
#         return [
#             c.Button(
#                 text=can.address_line1,
#                 on_click=e.GoToEvent(
#                     url=f'/hire/update/{manager.id}/{manager.state.update_dump_64_o(states.ShipStatePartial(address=can))}',
#                 ),
#                 class_name=am_styles.BUTTON,
#             )
#             for can in manager.state.address_candidates
#         ]
#
#     return c.Div(
#         components=[
#             c.Button(
#                 text='Choose Address',
#                 on_click=e.PageEvent(
#                     name='address-chooser',
#                 ),
#                 class_name=am_styles.BUTTON,
#             ),
#             c.Modal(
#                 title='Address',
#                 body=await address_chooser_buttons(),
#                 footer=[
#                     c.Button(text='Close', on_click=e.PageEvent(name='address-chooser', clear=True)),
#                 ],
#                 open_trigger=e.PageEvent(name='address-chooser'),
#             ),
#         ],
#         class_name=class_name,
#     )


async def date_modal_div(manager: managers.BookingManagerOut, class_name='row') -> c.Div:
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
                class_name=am_styles.BUTTON,
            )
            for ship_date in weekday_dates
        ]

    return c.Div(
        components=[
            c.Button(
                text=amui.date_string(manager.state.ship_date),
                on_click=e.PageEvent(
                    name='date-chooser',
                ),
                class_name=am_styles.BUTTON,
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
        class_name=class_name,
    )


async def booking_div(
        manager: managers.BookingManagerOut,
        direction: _t.Literal['in', 'out'],
        class_name='row'
) -> c.Div:
    return c.Div(
        components=[
            c.Button(
                text=f'Ship {direction.title()}Bound',
                on_click=e.PageEvent(name=f'ship-{direction}'),
                class_name=am_styles.BUTTON,
            ),
            c.Modal(
                title=f'Confirm {direction.title()}bound Shipping',
                body=[
                    c.Button(
                        text=f'Book {direction.title()}Bound',
                        on_click=e.GoToEvent(
                            url=f'/book/goanon/{direction}/{manager.id}',
                        ),
                        class_name=am_styles.BUTTON,
                    ),
                    await review_state(manager.state)
                ],
                footer=[
                    c.Button(
                        text='Close',
                        on_click=e.PageEvent(name=f'ship-{direction}', clear=True)
                    ),
                ],
                open_trigger=e.PageEvent(name=f'ship-{direction}'),
            ),
        ],
        class_name=class_name,
    )


async def review_state(state: shipr.ShipState) -> c.Div:
    # texts = builders.object_strs_texts(state, with_keys='YES')
    texts = builders.dict_strs_texts(state.model_dump(), with_keys='YES')
    return c.Div(
        components=builders.list_of_divs(
            components=texts
        ),
        class_name='row'
    )

# async def away_collection_row(manager_id: int) -> c.Div:
#     return c.Div(
#         components=[
#             c.Button(
#                 text='Away Collection',
#                 on_click=e.GoToEvent(
#                     url=f'/book/collection/{manager_id}',
#                 ),
#                 class_name=am_styles.BUTTON,
#             ),
#         ],
#     )

#


# async def inbound_modal_div(manager: managers.BookingManagerOut, class_name='row') -> c.Div:
#     return c.Div(
#         components=[
#             c.Button(
#                 text='Ship InBound',
#                 on_click=e.PageEvent(name='ship-in'),
#                 class_name=am_styles.BUTTON,
#             ),
#             c.Modal(
#                 title='Confirm Inbound Shipping',
#                 body=[
#                     c.Button(
#                         text='Book InBound',
#                         on_click=e.GoToEvent(
#                             url=f'/book/collection/{manager.id}',
#                         ),
#                         class_name=am_styles.BUTTON,
#                     ),
#                     await review_state(manager.state)
#                 ],
#                 footer=[
#                     c.Button(text='Close', on_click=e.PageEvent(name='ship-in', clear=True)),
#                 ],
#                 open_trigger=e.PageEvent(name='ship-in'),
#             ),
#         ],
#         class_name=class_name,
#     )


# async def outbound_modal_div(manager, class_name='row') -> c.Div:
#     return c.Div(
#         components=[
#             c.Button(
#                 text='Ship OutBound',
#                 on_click=e.PageEvent(name='ship-out'),
#                 class_name=am_styles.BUTTON,
#             ),
#             c.Modal(
#                 title='Confirm Outbound Shipping',
#                 body=[
#                     c.Button(
#                         text='Book OutBound',
#                         on_click=e.GoToEvent(
#                             url=f'/book/go/{manager.id}',
#                         ),
#                         class_name=am_styles.BUTTON,
#                     ),
#                     await review_state(manager.state)
# 
#                 ],
#                 footer=[
#                     c.Button(text='Close', on_click=e.PageEvent(name='ship-out', clear=True)),
#                 ],
#                 open_trigger=e.PageEvent(name='ship-out'),
#             ),
#         ],
#         class_name=class_name,
#     )
