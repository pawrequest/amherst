import typing as _t

import pydantic as _p
import sqlmodel
from fastapi import APIRouter, Depends
from fastui import FastUI, components as c, events, events as e, forms as fuiforms

from amherst import am_db
from amherst.routers import back_funcs
from pawdantic.pawui import builders
from shipr.ship_ui import forms as shipforms

router = APIRouter()

FormKind: _t.TypeAlias = _t.Literal['manual', 'select']  # noqa: UP040 fastui not support


@router.get('/{kind}/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def forms_view(
        manager_id: int,
        kind: FormKind = 'select',
        session=Depends(am_db.get_session)
) -> list[c.AnyComponent]:
    manager = await back_funcs.get_manager(manager_id, session)
    return await builders.page_w_alerts(
        components=[
            await left_col(manager),
            await right_col(kind, manager),
        ],
        title='Forms',
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
            return [
                c.Form(
                    form_fields=await shipforms.ship_fields_manual(manager.state),
                    submit_url=f'/api/forms/manual/{manager_id}',
                ),
            ]
        case 'select':
            return [
                c.Form(
                    form_fields=await shipforms.ship_fields_select(manager.state),
                    submit_url=f'/api/forms/select/{manager_id}',
                ),
            ]
        case _:
            raise ValueError(f'Invalid kind {kind!r}')


class LoginForm(_p.BaseModel):
    email: str = _p.Field(
        title='Email Address',
    )


@router.post('/login', response_model=FastUI, response_model_exclude_none=True)
async def login_form_post(form: _t.Annotated[LoginForm, fuiforms.fastui_form(LoginForm)]):
    print(form)
    return [c.FireEvent(event=e.GoToEvent(url='/'))]


async def left_col(manager) -> c.Div:
    return c.Div(
        class_name='col col-4 mx-auto',
        components=[
            await input_address_div(manager),
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


async def right_col(kind, manager) -> c.Div:
    with sqlmodel.Session(am_db.ENGINE) as session:
        return c.Div(
            class_name='col',
            components=[

                c.ServerLoad(
                    path=f'/forms/get_form/{manager.id}/{kind}',
                    load_trigger=e.PageEvent(name='change-form'),
                    components=await get_form(manager.id, kind, session),
                ),

                # c.Form(
                #     form_fields=await shipforms.ship_fields_select(manager.state),
                #     submit_url=f'/api/forms/big/{manager.id}',
                #
                # ),
                c.Button(
                    text='manual',
                    on_click=events.GoToEvent(url='/sp2/manual/1'),
                ),
                c.Button(
                    text='select',
                    on_click=events.GoToEvent(url='/sp2/select/1'),
                ),
                # await manual_entry_modal_div(manager),
            ]
        )
