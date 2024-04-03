from __future__ import annotations

import datetime

import fastapi
from fastui import components as c, events as e, events

from amherst.front import am_styles
from amherst.models import managers
from pawdantic import paw_strings
from pawdantic.pawui import builders, pawui_types, styles
from shipr.ship_ui import forms as ship_forms, states

router = fastapi.APIRouter()


async def ship_page(
        manager: managers.BOOKED_MANAGER,
        alert_dict: pawui_types.AlertDict | None = None,
        manual_entry=False,
) -> list[
    c.AnyComponent]:
    alert_dict = alert_dict or {}
    state_alerts = manager.state.alert_dict or {}
    alert_dict.update(state_alerts)
    return await builders.page_w_alerts(
        alert_dict=alert_dict,
        # page_class_name=',
        container_class_name='container container-flex mt-2',
        components=[c.Div(
            components=[
                await left_col(manager),
                # await right_col(manager),
                # *((await right_col_manual(manager),) if manual_entry else await right_col_no_manual(manager),),
                await right_col(manager),
            ],
            class_name='row my-3',
        )],
    )


async def left_col(manager) -> c.Div:
    return c.Div(
        class_name='col col-4 mx-auto',
        components=[
            await input_address_div(manager),
            # await address_form_select(manager),
            await address_from_pc_div(manager),
            # await boxes_modal_row(manager),
            # await boxes_enum_select(manager.id),
            # await boxes_form(manager),
            # await date_modal_div(manager),
            # await invoice_div(manager),
            # await booking_div(manager, 'in'),
            # await booking_div(manager, 'out'),
        ],
    )


async def right_col(manager) -> c.Div:
    return c.Div(
        class_name='col',
        components=[
            c.Form(
                form_fields=await ship_forms.ship_fields_select(manager.state),
                submit_url=f'/api/forms/big/{manager.id}',

            ),
            c.Button(
                text='manual',
                on_click=events.GoToEvent(url='/sp2/manual/1'),
            ),
            # await manual_entry_modal_div(manager),
        ]
    )


async def right_col_manual(manager) -> c.Div:
    return c.Div(
        class_name='col',
        components=[
            # await clickme_div(manager.model_dump_json()),

            c.Form(
                form_fields=await ship_forms.ship_fields_manual(manager.state),
                submit_url=f'/api/forms/big/{manager.id}',

            ),
            await manual_entry_modal_div(manager),
        ]
    )


async def right_col_no_manual(manager) -> c.Div:
    return c.Div(
        class_name='col',
        components=[
            # await clickme_div(manager.model_dump_json()),

            c.Form(
                form_fields=await ship_forms.ship_fields_select(manager.state),
                submit_url=f'/api/forms/big/{manager.id}',

            ),
            c.Button(
                text='Manual Entry',
                on_click=e.GoToEvent(
                    url=f'/ship/view_manual/{manager.id}',
                    query={'manual_entry': True},
                )
            )
        ]
    )


# async def right_col_ssl(manager):
#     return c.Div(
#         class_name='col',
#         components=[
#             await clickme_div(manager.model_dump_json()),
#
#             c.Form(
#                 form_fields=await ship_forms.big_form_fields(manager.state),
#                 submit_url=f'/api/forms/big/{manager.id}',
#
#             ),
#         ]
#     )


async def address_form_select(manager):
    return c.Form(
        form_fields=[await ship_forms.address_select(manager.state)],
        submit_url=f'/api/forms/address_form/{manager.id}',

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
                        model=ship_forms.PostcodeSelect,
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


async def date_modal_div(manager: managers.BookingManagerOut, class_name='row') -> c.Div:
    async def date_chooser_buttons() -> list[c.AnyComponent]:
        start_date = datetime.date.today()
        date_range = [start_date + datetime.timedelta(days=x) for x in range(7)]
        weekday_dates = [d for d in date_range if d.weekday() < 5]  # 0-4 are weekdays

        return [
            c.Button(
                text=paw_strings.date_string(ship_date),
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
                text=paw_strings.date_string(manager.state.ship_date),
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


async def address_chooser(
        manager: managers.BOOKED_MANAGER,
) -> list[c.AnyComponent]:
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
            for can in manager.state.candidates
        ],
        title='addresses',
    )


async def manual_entry_modal_div(manager: managers.BOOKED_MANAGER) -> c.Div:
    return c.Div(
        components=[
            c.Button(
                text='Manual Entry',
                on_click=e.PageEvent(name='manual-entry'),
                class_name=am_styles.BUTTON,
            ),
            c.Modal(
                title='Manual Entry',
                body=[
                    c.ModelForm(
                        model=ship_forms.AddressForm,
                        initial=manager.state.address.model_dump(),
                        submit_url=f'/api/forms/address/{manager.id}',
                    ),
                ],
                footer=[
                    c.Button(text='Close', on_click=e.PageEvent(name='manual-entry', clear=True)),
                ],
                open_trigger=e.PageEvent(name='manual-entry'),
            ),
        ],
        class_name=styles.ROW_STYLE,
    )
