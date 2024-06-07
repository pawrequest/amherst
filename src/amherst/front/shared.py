from __future__ import annotations, annotations

import base64
import os

import sqlmodel
from fastapi import APIRouter, Depends
from fastui import FastUI, components as c, events, events as e
from loguru import logger
from pawdantic.pawui import builders

from amherst import am_db
from amherst.front import emailer, support
from amherst.front.ship import shipping_page
from amherst.models.shipment_record import ShipmentRecordInDB, ShipmentRecordOut

router = APIRouter()


# @router.get('/fail/', response_model=FastUI, response_model_exclude_none=True)
@router.get('/fail/{alert}', response_model=FastUI, response_model_exclude_none=True)
async def fail_page(
        alert: str
) -> support.Fui_Page:
    alert = base64.urlsafe_b64decode(alert).decode('utf-8')
    logger.warning(f'ERROR {alert}')
    return await builders.page_w_alerts(
        alert_dict={alert: 'ERROR'},
        components=[
            # c.Text(text='Error Page')
        ],
        title='ERROR',
    )


@router.get('/invoice/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def open_invoice(
        manager_id: int,
        session: sqlmodel.Session = Depends(am_db.get_session),
) -> support.Fui_Page:
    """Endpoint for opening invoice.

    Opens invoice file for the shipable_item in the booking shiprec.

    Args:
        manager_id: Booking Manager ID
        session: sqlmodel session

    Returns:
        Redirects to Shipping page with alert if invoice not found.

    """
    man_in = await support.get_shiprec(manager_id, session)
    inv_file = await support.get_invoice_path(man_in.record)
    man_out = ShipmentRecordOut.model_validate(man_in)

    try:
        os.startfile(inv_file)
    except (FileNotFoundError, TypeError):
        logger.error(f'Invoice file not found: {inv_file}')
        return await shipping_page.ship_page(
            manager=man_out,
            alert_dict={'INVOICE NOT FOUND': 'WARNING'}
        )

    return [c.FireEvent(event=events.GoToEvent(url=f'/ship/select/{manager_id}'))]


@router.get('/invoice2/{shiprec_id}', response_model=FastUI, response_model_exclude_none=True)
async def open_invoice2(
        shiprec_id: int,
        session: sqlmodel.Session = Depends(am_db.get_session),
) -> c.AnyComponent:
    """Endpoint for opening invoice.

    Opens invoice file for the shipable_item in the booking shiprec.

    Args:
        shiprec_id: Booking Manager ID
        session: sqlmodel session

    Returns:
        Redirects to Shipping page with alert if invoice not found.

    """
    shiprec = await support.get_shiprec(shiprec_id, session)
    inv_file = await support.get_invoice_path(shiprec.record)
    man_out = ShipmentRecordOut.model_validate(shiprec)

    try:
        os.startfile(inv_file)
    except (FileNotFoundError, TypeError):
        logger.error(f'Invoice file not found: {inv_file}')
        # return await shipping_page(
        #     shiprec_id=shiprec_id,
        #     session=session,
        #     alert_dict={'INVOICE NOT FOUND': 'WARNING'}
        # )
        return [c.Text(text='Invoice Not Found')]

    return [c.Text(text='Invoice Opened')]
    # return [c.FireEvent(event=events.GoToEvent(url=f'/ship/select/{shiprec_id}'))]


async def invoice_div(shiprec: ShipmentRecordOut) -> c.Div:
    """Div for opening invoice.

    Args:
        shiprec: Booking Manager

    Returns:
        c.Div: Div with button to fire GoToEvent to invoice endpoint

    """
    return c.Div(
        class_name='row mx-auto my-3',
        components=[
            c.Button(
                text='Open Invoice',
                on_click=e.GoToEvent(
                    url=f'/shared/invoice/{shiprec.id}',
                ),
                # on_click=e.PageEvent(
                #     name='open_invoice',
                # ),
            ),
            # await get_sse(shiprec.id),
        ],
    )


async def get_sse(shiprec_id):
    c.ServerLoad(
        # not fstring!!!!!
        path=f'/shared/invoice2/{shiprec_id}',
        load_trigger=e.PageEvent(name='open-invoice'),
        components=[c.Text(text='Invoice Openedsasss')],
        # components=[await open_invoice2(shiprec_id)],
    )


async def email_div(shiprec: ShipmentRecordInDB, choices: list[support.EmailChoices]):
    return c.Div(class_name='row my-3', components=[emailer.get_email_form(shiprec, choices)])


async def close_div():
    """Html Div with button to close the application."""
    return c.Div(
        class_name='row my-3',
        components=[
            c.Button(
                text='Close Application',
                on_click=e.GoToEvent(
                    url='/close_app/',
                ),
                class_name='btn btn-lg btn-primary',
            )
        ],
    )
