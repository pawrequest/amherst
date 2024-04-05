import typing as _t

import fastapi
from fastapi import APIRouter
from fastui import FastUI, components as c, events as e
from fastui.forms import fastui_form
from loguru import logger

from amherst import am_db, shipper
from amherst.front import support
from amherst.front.support import ModelKind
from pawdantic.pawui import builders
from shipr.models import pf_top

router = APIRouter()


@router.get('/{kind}/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def forms_view(kind: ModelKind, manager_id: int) -> list[c.AnyComponent]:
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
                components=await get_form(kind, manager_id),
            ),
        ],
    )


@router.get(
    '/get_form/{kind}/{manager_id}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def get_form(kind: ModelKind, manager_id: int):
    logger.debug(f'getting form for {kind}')
    form_model = await support.get_model_form_type(kind)

    return [
        c.ModelForm(
            model=form_model,
            submit_url=f'/api/ship_model/{kind}/{manager_id}'
        )
    ]


@router.post('/zero/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def zero_post(
        manager_id: int,
        form: _t.Annotated[
            pf_top.RequestedShipmentZero, fastui_form(pf_top.RequestedShipmentZero)],
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),

):
    print(form)

    return [c.Text(text='zero post')]


@router.post('/minimum/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def minimum_post(
        manager_id: int,
        form: _t.Annotated[
            pf_top.RequestedShipmentMinimum, fastui_form(pf_top.RequestedShipmentMinimum)],
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),

):
    print(form)

    return [c.Text(text='minimum post')]


@router.post('/simple/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def simple_post(
        manager_id: int,
        form: _t.Annotated[
            pf_top.RequestedShipmentSimple, fastui_form(pf_top.RequestedShipmentSimple)],
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),

):
    print(form)

    return [c.Text(text='simple post')]
