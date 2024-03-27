from __future__ import annotations

import datetime

import fastapi
from fastui import FastUI
from fastui import components as c
from fastui import events as e

from amherst.front import am_styles
from amherst.models import managers
from pawdantic import paw_strings, paw_types
from pawdantic.pawui import builders, pawui_types, styles
from shipr.ship_ui import forms as ship_forms
from shipr.ship_ui import states

router = fastapi.APIRouter()


async def ship_page(
        manager: managers.BOOKED_MANAGER,
        alert_dict: pawui_types.AlertDict | None = None
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
            await address_form_select(manager),
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


async def right_col(manager):
    return c.Div(
        class_name='col',
        components=[
            # await clickme_div(manager.model_dump_json()),

            c.Form(
                form_fields=await ship_forms.big_form_fields(manager.state),
                submit_url=f'/api/forms/big/{manager.id}',

            ),
        ]
    )


async def address_form_select(manager):
    return c.Form(
        form_fields=[await ship_forms.address_f_postcode_select_field(manager.state)],
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


# async def booking_div(
#         manager: managers.BookingManagerOut,
#         direction: _t.Literal['in', 'out'],
#         class_name='row'
# ) -> c.Div:
#     return c.Div(
#         components=[
#             c.Button(
#                 text=f'Ship {direction.title()}Bound',
#                 on_click=e.PageEvent(name=f'ship-{direction}'),
#                 class_name=amherst.front.am_styles.BUTTON,
#             ),
#             c.Modal(
#                 title=f'Confirm {direction.title()}bound Shipping',
#                 body=[
#                     c.Button(
#                         text=f'Book {direction.title()}Bound',
#                         on_click=e.GoToEvent(
#                             url=f'/book/go_book/{direction}/{manager.id}',
#                         ),
#                         class_name=amherst.front.am_styles.BUTTON,
#                     ),
#                     c.ServerLoad(path=f'/sl/check_state/{manager.id}')
#                 ],
#                 footer=[
#                     c.Button(
#                         text='Close',
#                         on_click=e.PageEvent(name=f'ship-{direction}', clear=True)
#                     ),
#                 ],
#                 open_trigger=e.PageEvent(name=f'ship-{direction}'),
#             ),
#         ],
#         class_name=class_name,
#     )


#####
####
####

# async def boxes_modal_row(manager: managers.BOOKED_MANAGER) -> c.Div:
#     return c.Div(
#         components=[
#             c.Button(
#                 text=f'{manager.state.boxes} Boxes',
#                 on_click=e.PageEvent(name='manual-entry'),
#                 class_name=amherst.front.am_styles.BUTTON,
#             ),
#             c.Modal(
#                 title='Manual Address and Contact Entry',
#                 body=await boxes_chooser_button_rows(),
#                 footer=[
#                     c.Button(text='Close', on_click=e.PageEvent(name='manual-entry', clear=True)),
#                 ],
#                 open_trigger=e.PageEvent(name='manual-entry'),
#             ),
#         ],
#         class_name=styles.ROW_STYLE,
#     )
# 
# 
# async def boxes_enum_select(manager_id):
#     return c.Div(
#         components=[
#             c.ModelForm(
#                 model=dynamic.BoxesModelForm,
#                 submit_url=f'/api/forms/boxes/{manager_id}',
# 
#             )
#         ],
#     )
# 
# 


# 
# async def manual_entry_modal(manager: managers.BOOKED_MANAGER) -> c.Div:
#     return c.Div(
#         components=[
#             c.Button(
#                 text='Manual Entry',
#                 on_click=e.PageEvent(name='manual-entry'),
#                 class_name=amherst.front.am_styles.BUTTON,
#             ),
#             c.Modal(
#                 title='Manual Entry',
#                 body=[
#                     c.ModelForm(
#                         model=ship_forms.AddressForm,
#                         initial=manager.state.address.model_dump(),
#                         submit_url=f'/api/forms/address/{manager.id}',
#                     ),
#                 ],
#                 footer=[
#                     c.Button(text='Close', on_click=e.PageEvent(name='manual-entry', clear=True)),
#                 ],
#                 open_trigger=e.PageEvent(name='manual-entry'),
#             ),
#         ],
#         class_name=styles.ROW_STYLE,
#     )

# class DateEnum(str, Enum):
#     TODAY = datetime.date.today()
#


# return c.ServerLoad(path=f'/sl/booking_form/{manager.id}')


# async def right_col(manager):
#     return c.Div(
#         components=[
#             c.ModelForm(
#                 model=ship_forms.ContactAndAddressForm,
#                 initial=paw_types.multi_model_dump(
#                     manager.state.contact,
#                     manager.state.address,
#                 ),
#                 submit_url=f'/api/forms/address_contact/{manager.id}',
#                 class_name='row h6',
#                 submit_on_change=True,
#             ),
#         ],
#         class_name='col',
#     )

#
# async def right_col2(manager):
#     return c.Div(
#         components=[
#             c.ModelForm(
#                 model=ship_forms.FullForm,
#                 initial={
#                     'boxes': manager.state.boxes,
#                     'ship_date': manager.state.ship_date,
#                     'direction': manager.state.direction,
#                     **paw_types.multi_model_dump(
#                         manager.state.contact,
#                         manager.state.address,
#                     )
#                 },
#                 submit_url=f'/api/forms/big/{manager.id}',
#                 class_name='row h6',
#                 submit_on_change=True,
#             ),
#         ],
#         class_name='col',
#     )

# async def boxes_form(manager):
#     return c.Form(
#         form_fields=[
#             c.FormFieldSelect(
#                 name='boxes',
#                 title='Boxes',
#                 required=True,
#                 options=[
#                     fastui_forms.SelectOption(value=str(i), label=str(i))
#                     for i in range(1, 11)
#                 ],
#                 initial=str(manager.state.boxes),
#             ),
#         ],
#         submit_url=f'/api/forms/boxes/{manager.id}',
#         submit_on_change=True,
#
#     )


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

