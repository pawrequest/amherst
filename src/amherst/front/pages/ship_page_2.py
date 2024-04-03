import typing as _t

import sqlmodel
from fastapi import APIRouter, Depends
from fastui import FastUI, components as c, events, events as e

from amherst import am_db
from amherst.front import am_styles
from amherst.routers import back_funcs
from pawdantic.pawui import builders, pawui_types
from shipr.ship_ui import forms as shipforms

router = APIRouter()

FormKind: _t.TypeAlias = _t.Literal['manual', 'select']  # noqa: UP040 fastui not support


@router.get('/{kind}/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def shipping_page(
        manager_id: int,
        kind: FormKind = 'select',
        session=Depends(am_db.get_session),
        alert_dict: pawui_types.AlertDict | None = None,
) -> list[c.AnyComponent]:
    manager = await back_funcs.get_manager(manager_id, session)
    return await builders.page_w_alerts(
        alert_dict=alert_dict,
        components=[
            await left_col(manager),
            await right_col(kind, manager),
        ],
        title='Forms',
    )


async def left_col(manager) -> c.Div:
    return c.Div(
        class_name='col col-4 mx-auto',
        components=[
            await input_address_div(manager),
            # await address_from_pc_div(manager),
        ],
    )


async def right_col(kind, manager) -> c.Div:
    with sqlmodel.Session(am_db.ENGINE) as session:
        return c.Div(
            class_name='col',
            components=[
                await serverload_form_div(kind, manager, session),
                # await form_select_div(),
            ]
        )


async def form_select_div():
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                class_name='col mx-2 btn btn-primary',
                text='Manual Address Override',
                on_click=events.GoToEvent(url='/sp2/manual/1'),
            ),
            c.Button(
                class_name='col mx-2 btn btn-primary',
                text='Select Address From Postcode',
                on_click=events.GoToEvent(url='/sp2/select/1'),
            )
        ],
    )


async def serverload_form_div(kind: FormKind, manager, session):
    match kind:
        case 'manual':
            button_text = 'Select Address From Postcode'
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
                on_click=events.GoToEvent(url=f'/sp2/{other_kind}/1'),
            ),
        ]
    )


@router.get(
    '/get_form/{manager_id}/{kind}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def get_form(manager_id: int, kind: FormKind, session=Depends(am_db.get_session)):
    manager = await back_funcs.get_manager(manager_id, session)
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
            c.Div(
                components=[

                    c.ModelForm(
                        model=shipforms.PostcodeSelect,
                        initial={'fetch_address_from_postcode': manager.state.address.postcode},
                        submit_url=f'/api/forms/postcode/{manager.id}',
                        class_name='row h6',
                    ),

                ],
                class_name='row mx-auto my-3',
            )
        ],
        class_name='row mx-auto',
    )
