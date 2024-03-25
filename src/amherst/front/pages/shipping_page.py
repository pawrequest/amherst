from __future__ import annotations

import datetime as dt
import typing as _t

from fastui import AnyComponent, components as c, events as e, forms as fastui_forms

import pawdantic.paw_strings
from amherst.front import styles as am_styles
from amherst.models import managers
from pawdantic import paw_types
from pawdantic.pawui import builders, pawui_types, styles
from shipr.models import pf_ext
from shipr.models.dynamic import BoxesModelForm
from shipr.models.types import PostcodeSelect
from shipr.ship_ui import forms as ship_forms, states


async def ship_page(
        manager: managers.BookingManagerOut,
        alert_dict: pawui_types.AlertDict | None = None
) -> list[
    c.AnyComponent]:
    alert_dict = alert_dict or {}
    state_alerts = manager.state.alert_dict or {}
    alert_dict.update(state_alerts)
    return await builders.page_w_alerts(
        alert_dict=alert_dict,
        page_class_name=am_styles.PAGE_STYLE,
        container_class_name=am_styles.CONTAINER_STYLE,
        components=[c.Div(
            components=[
                await left_col(manager),
                # await right_col(manager),
                await right_col2(manager),
            ],
            class_name='row my-3',
        )],
    )


async def left_col(manager) -> c.Div:
    return c.Div(
        class_name='col col-4 mx-auto',
        components=[
            await input_address_div(manager),
            # await boxes_modal_row(manager),
            # await boxes_enum_select(manager.id),
            await boxes_form(manager),
            await date_modal_div(manager),
            await invoice_div(manager),
            await booking_div(manager, 'in'),
            await booking_div(manager, 'out'),
            await address_from_pc_div(manager),
            await big_book_form_div(manager),
        ],
    )


def get_dates() -> list[fastui_forms.SelectOption]:
    return [
        fastui_forms.SelectOption(
            value=str(d.isoformat()),
            label=pawdantic.paw_strings.date_string(d),
        )
        for d in [dt.date.today() + dt.timedelta(days=i) for i in range(7)]
    ]


def get_addresses(candidates: list[pf_ext.AddressRecipient]) -> list[fastui_forms.SelectOption]:
    return [
        fastui_forms.SelectOption(
            value=cand.model_dump_json(),
            label=cand.address_line1,
        )
        for cand in candidates
    ]


async def big_book_form_div(manager):
    # return c.ServerLoad(path=f'/sl/booking_form/{manager.id}')
    return c.Div(
        class_name='row',
        components=[
            c.Form(
                form_fields=[
                    c.FormFieldSelect(
                        name='date',
                        options=get_dates(),
                        initial=str(manager.state.ship_date.isoformat()),
                        title='date',
                    ),
                    c.FormFieldSelect(
                        name='boxes',
                        options=[
                            fastui_forms.SelectOption(value=str(i), label=str(i))
                            for i in range(1, 11)
                        ],
                        initial=str(manager.state.boxes),
                        title='boxes',
                    ),
                    c.FormFieldSelect(
                        name='direction',
                        title='direction',
                        options=[
                            fastui_forms.SelectOption(value='in', label='Inbound'),
                            fastui_forms.SelectOption(value='out', label='Outbound'),
                        ],
                        initial='out',
                    ),
                    c.FormFieldSelect(
                        name='address_from_postcode',
                        options=get_addresses(manager.state.candidates),
                        title='Address From Postcode',
                        initial=manager.state.address.model_dump_json(),
                    ),
                    # c.FormField(
                    #     name='ship_service',
                    #     label='Service',
                    #     input_type='text',
                    #     value=manager.state.ship_service,
                    # ),
                ],
                submit_url=f'/api/forms/book_form/{manager.id}',

            ),
        ]
    )


async def right_col(manager):
    return c.Div(
        components=[
            c.ModelForm(
                model=ship_forms.ContactAndAddressForm,
                initial=paw_types.multi_model_dump(
                    manager.state.contact,
                    manager.state.address,
                ),
                submit_url=f'/api/forms/address_contact/{manager.id}',
                class_name='row h6',
                submit_on_change=True,
            ),
        ],
        class_name='col',
    )


async def right_col2(manager):
    return c.Div(
        components=[
            c.ModelForm(
                model=ship_forms.FullForm,
                initial={
                    'boxes': manager.state.boxes,
                    'ship_date': manager.state.ship_date,
                    'direction': manager.state.direction,
                    **paw_types.multi_model_dump(
                        manager.state.contact,
                        manager.state.address,
                    )
                },
                submit_url=f'/api/forms/big/{manager.id}',
                class_name='row h6',
                submit_on_change=True,
            ),
        ],
        class_name='col',
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


async def address_from_pc_div(manager) -> c.Div:
    return c.Div(
        components=[
            c.Div(
                components=[

                    c.ModelForm(
                        model=PostcodeSelect,
                        initial={'fetch_address_from_postcode': manager.state.address.postcode},
                        submit_url=f'/api/forms/postcode/{manager.id}',
                        class_name='row h6',
                    ),

                ],
                class_name=am_styles.BUTTON,
            )
        ],
        class_name='row mx-auto',
    )


async def invoice_div(manager: managers.BookingManagerOut) -> c.Div:
    return c.Div(
        components=[
            c.Button(
                text='Open Invoice',
                on_click=e.GoToEvent(
                    url=f'/ship/invoice/{manager.id}',
                ),
            )
        ],
        class_name=styles.ROW_STYLE,
    )


async def boxes_form(manager):
    return c.Form(
        form_fields=[
            c.FormFieldSelect(
                name='boxes',
                title='Boxes',
                required=True,
                options=[
                    fastui_forms.SelectOption(value=str(i), label=str(i))
                    for i in range(1, 11)
                ],
                initial=str(manager.state.boxes),
            ),
        ],
        submit_url=f'/api/forms/boxes/{manager.id}',
        submit_on_change=True,

    )


async def boxes_enum_select(manager_id):
    return c.Div(
        components=[
            c.ModelForm(
                model=BoxesModelForm,
                submit_url=f'/api/forms/boxes/{manager_id}',

            )
        ],
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
                            url=f'/ship/update/{manager.id}/{manager.state.update_dump_64_o(states.ShipStatePartial(address=can))}',
                        ),
                    )
                ],
            )
            for can in candidates
        ],
        title='addresses',
    )


async def address_chooser2(
        manager: managers.BookingManagerOut, candidates: list[pf_ext.AddressRecipient]
):
    return c.Form(
        form_fields=[
            c.FormFieldSelect(
                name='address',
                options=[
                    fastui_forms.SelectOption(
                        value=can.model_dump_json(),
                        label=can.address_line1,
                    )
                    for can in candidates
                ],
                initial=manager.state.address.model_dump_json(),
                title='address',
            ),
        ],
        submit_url=f'/api/forms/address_select/{manager.id}',
    )


async def date_modal_div(manager: managers.BookingManagerOut, class_name='row') -> c.Div:
    async def date_chooser_buttons() -> list[c.AnyComponent]:
        start_date = dt.date.today()
        date_range = [start_date + dt.timedelta(days=x) for x in range(7)]
        weekday_dates = [d for d in date_range if d.weekday() < 5]  # 0-4 are weekdays

        return [
            c.Button(
                text=pawdantic.paw_strings.date_string(ship_date),
                on_click=e.GoToEvent(
                    url=f'/ship/update/{manager.id}/{manager.state.update_dump_64_o(states.ShipStatePartial(ship_date=ship_date))}',
                ),
                class_name=am_styles.BUTTON,
            )
            for ship_date in weekday_dates
        ]

    return c.Div(
        components=[
            c.Button(
                text=pawdantic.paw_strings.date_string(manager.state.ship_date),
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
                            url=f'/book/go_book/{direction}/{manager.id}',
                        ),
                        class_name=am_styles.BUTTON,
                    ),
                    c.ServerLoad(path=f'/sl/check_state/{manager.id}')
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


async def boxes_modal_row(manager: managers.BookedManager) -> c.Div:
    async def boxes_chooser_button_rows() -> list[c.Div]:
        return builders.list_of_divs(
            class_name='row',
            components=[
                c.Button(
                    text=str(i),
                    on_click=e.GoToEvent(
                        url=f'/ship/update/{manager.id}/{manager.state.update_dump_64(boxes=i)}',
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
