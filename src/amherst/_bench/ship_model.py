import typing as _t

import fastapi
import sqlmodel
from fastapi import APIRouter
from fastui import FastUI, components as c, events as e
from fastui.forms import fastui_form
from loguru import logger

import amherst._bench.benched_types
import amherst.front.forms
from amherst import am_db
from amherst.front import support
from amherst._bench.benched_types import ModelKind
from pawdantic.pawui import builders
from shipaw.models import pf_top

router = APIRouter()


@router.get('/{kind}/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def forms_view(
        kind: ModelKind,
        manager_id: int,
        session: sqlmodel.Session = fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    """Endpoint returning """
    return await builders.page_w_alerts(
        components=[
            c.LinkList(
                links=[
                    c.Link(
                        components=[c.Text(text='Zero Form')],
                        on_click=e.PageEvent(
                            name='change-form',
                            push_path=f'/ship_model/zero/{manager_id}',
                            context={'kind': 'zero', 'manager_id': manager_id},
                        ),
                        active=f'/ship_model/zero/{manager_id}',
                    ),
                    c.Link(
                        components=[c.Text(text='Minimal Form')],
                        on_click=e.PageEvent(
                            name='change-form',
                            push_path=f'/ship_model/minimum/{manager_id}',
                            context={'kind': 'minimum', 'manager_id': manager_id},
                        ),
                        active=f'/ship_model/minimum/{manager_id}',
                    ),
                ],
                mode='tabs',
                class_name='+ mb-4',
            ),
            c.ServerLoad(
                # not fstring!!!!!
                path='/ship_model/get_form/{kind}/{manager_id}',
                load_trigger=e.PageEvent(name='change-form'),
                components=await get_form(kind, manager_id, session),
            ),
        ],
    )


async def get_initial(manager, form_model) -> dict:
    update = {
        k: v for k, v in manager.shipment.model_dump(exclude_none=True).items()
        if k in form_model.model_fields
    }
    return update


@router.get(
    '/get_form/{kind}/{manager_id}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def get_form(
        kind: ModelKind,
        manager_id: int,
        session: sqlmodel.Session = fastapi.Depends(am_db.get_session),
):
    manager = await support.get_manager(manager_id, session)
    logger.debug(f'getting form for {kind}')
    form_model = await amherst.front.forms.get_model_form_type(kind)

    model_initial = await get_initial(manager, form_model)
    return [
        c.ModelForm(
            model=form_model,
            submit_url=f'/api/ship_model/{kind}/{manager_id}',
            # initial=model_initial,
        )
    ]


