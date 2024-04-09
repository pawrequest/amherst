import os

import fastui
import sqlmodel
from fastapi import APIRouter, Depends
from fastui import FastUI, components as c, events, events as e
from loguru import logger

from amherst import am_db
from amherst.front import support
from amherst.models import managers
from pawdantic.pawui import builders, pawui_types
from shipr.ship_ui import forms as shipforms, states

router = APIRouter()


@router.get('/{kind}/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def shipping_page(
        manager_id: int,
        kind: support.FormKind = 'select',
        session=Depends(am_db.get_session),
        alert_dict: pawui_types.AlertDict | None = None,
) -> support.Fui_Page:
    manager = await support.get_manager(manager_id, session)
    return await builders.page_w_alerts(
        alert_dict=alert_dict,
        components=[
            await left_col(manager),
            await right_col(kind, manager),
        ],
        title='Forms',
    )


@router.get('/invoice/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def open_invoice(
        manager_id: int,
        session: sqlmodel.Session = Depends(am_db.get_session),
) -> support.Fui_Page:
    """Endpoint for opening/emailing invoice to the customer."""
    man_in = await support.get_manager(manager_id, session)
    inv_file = await support.get_invoice_path(man_in)
    man_out = managers.BookingManagerOut.model_validate(man_in)

    try:
        os.startfile(inv_file)
    except (FileNotFoundError, TypeError):
        logger.error(f'Invoice file not found: {inv_file}')
        return await shipping_page.ship_page(
            manager=man_out,
            alert_dict={'INVOICE NOT FOUND': 'WARNING'}
        )

    return [c.FireEvent(event=events.GoToEvent(url=f'/ship/select/{manager_id}'))]


async def left_col(manager) -> c.Div:
    return c.Div(
        class_name='col col-4 mx-auto',
        components=[
            await input_address_div(manager),
            await invoice_div(manager),
            # await address_from_pc_div(manager),

        ],
    )


async def right_col(kind, manager) -> c.Div:
    with sqlmodel.Session(am_db.get_engine()) as session:
        return c.Div(
            class_name='col',
            components=[
                await form_div_sl(kind, manager, session),
                # await form_select_div(),
            ]
        )


async def form_div_sl(kind: support.FormKind, manager, session):
    match kind:
        case 'manual':
            button_text = 'Choose Address From Postcode'
            other_kind = 'select'
        case 'select':
            button_text = 'Manual Address Override'
            other_kind = 'manual'
        case _:
            raise ValueError(f'Invalid kind {kind!r}')
    return c.Div(
        class_name='row my-3',
        components=[
            c.ServerLoad(
                path=f'/forms/get_form/{manager.id}/{kind}',
                load_trigger=e.PageEvent(name='change-form'),
                components=await get_form(manager.id, kind, session),
            ),

            c.Button(
                class_name='col col-4 my-3 btn btn-primary',
                text=button_text,
                on_click=events.GoToEvent(url=f'/ship/{other_kind}/1'),
            ),
        ]
    )


@router.get(
    '/get_form/{manager_id}/{kind}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def get_form(manager_id: int, kind: support.FormKind, session=Depends(am_db.get_session)):
    manager = await support.get_manager(manager_id, session)
    match kind:
        case 'manual':
            form_fields = await shipforms.ship_fields_manual(manager.state)
            submit_url = f'/api/forms/manual/{manager_id}'
        case 'select':
            form_fields = await shipforms.ship_fields_select(manager.state)
            submit_url = f'/api/forms/select/{manager_id}'
        case _:
            raise ValueError(f'Invalid kind {kind!r}')

    return [
        c.Form(
            form_fields=form_fields,
            submit_url=submit_url,
        ),
    ]


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
            c.Form(
                form_fields=[
                    c.FormFieldInput(
                        name='fetch_address_from_postcode',
                        title='Postcode',
                    ),
                ],
                submit_url=f'/api/forms/postcode2/{manager.id}',
            ),
        ],
        class_name='row mx-auto my-3',
    )


async def invoice_div(manager: managers.BookingManagerOut) -> c.Div:
    return c.Div(
        class_name='row mx-auto my-3',
        components=[
            c.Button(
                text='Open Invoice',
                on_click=e.GoToEvent(
                    url=f'/ship/invoice/{manager.id}',
                ),

            )
        ],
    )


# async def form_select_div():
#     return c.Div(
#         class_name='row my-3',
#         components=[
#             c.Button(
#                 class_name='col mx-2 btn btn-primary',
#                 text='Manual Address Override',
#                 on_click=events.GoToEvent(url='/ship/manual/1'),
#             ),
#             c.Button(
#                 class_name='col mx-2 btn btn-primary',
#                 text='Select Address From Postcode',
#                 on_click=events.GoToEvent(url='/ship/select/1'),
#             )
#         ],
#     )


# async def address_from_pc_div(manager) -> c.Div:
#     return c.Div(
#         components=[
#             c.Div(
#                 components=[
# 
#                     c.ModelForm(
#                         model=shipforms.PostcodeSelect,
#                         initial={'fetch_address_from_postcode': manager.state.address.postcode},
#                         submit_url=f'/api/forms/postcode/{manager.id}',
#                         class_name='row h6',
#                     ),
# 
#                 ],
#                 class_name='row mx-auto my-3',
#             )
#         ],
#         class_name='row mx-auto',
#     )


@router.get(
    '/update/{booking_id}/{update_64}',
    response_model=fastui.FastUI,
    response_model_exclude_none=True
)
async def update_shipment(
        booking_id: int,
        update_64: str | None = None,
        session: sqlmodel.Session = Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    updt = states.ShipStatePartial.model_validate_64(update_64)
    man_out = await support.update_and_commit(booking_id, updt, session)
    return await shipping_page(manager=man_out)


async def special_instructions_div(manager: managers.MANAGER_IN_DB) -> c.Div:
    return c.Div(
        class_name='row',
        components=[
            c.Button(
                text='Special Instructions',
                on_click=e.PageEvent(name='special-instructions'),
                class_name='btn btn-lg btn-primary',
            ),
            c.Modal(
                title='Special Instructions',
                body=[
                    c.ModelForm(
                        model=shipforms.AddressForm,
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
    )
