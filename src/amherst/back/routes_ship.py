from fastapi import APIRouter, Body, Depends, Form
from fastapi.encoders import jsonable_encoder
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressBase, AddressChoice
from shipaw.models.pf_msg import ShipmentResponse
from shipaw.ship_types import VALID_POSTCODE

from amherst.back.backend_search_paginate import record_from_json_str_form
from amherst.back.backend_shipper import (
    book_shipment,
    get_el_client,
    shipment_from_record,
    shipment_f_form,
    shipment_str_form_to_shipment,
    wait_label,
)
from amherst.back.backend_pycommence import get_one
from amherst.config import TEMPLATES
from amherst.models.amherst_models import AMHERST_TABLE_MODELS, AmherstShipment, AmherstTableBase

router = APIRouter()


async def record_to_form(request, record: AmherstTableBase, html='ship/form_shape.html'):
    shipment = await shipment_from_record(record)
    jsonable_ship = jsonable_encoder(shipment)
    jsonable_record = jsonable_encoder(record)
    # record_str = record.model_dump_json()
    return TEMPLATES.TemplateResponse(
        html,
        {
            'request': request,
            'shipment': jsonable_ship,
            'record': jsonable_record,
            # 'record_str': record_str,
        },
    )


@router.get('/form', response_class=HTMLResponse)
async def ship_form_extends(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(get_one),
    # SearchRequest
):
    logger.debug(f'SHIP Extended ROW ID: {record.row_id}')
    return await record_to_form(request, record, html='ship/form_shape.html')


@router.get('/form_content', response_class=HTMLResponse)
async def ship_form_content(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(get_one),
    # SearchRequest w row_id
):
    logger.debug(f'SHIP FROM ROW ID: {record.row_id}')
    return await record_to_form(request, record, html='ship/form_content.html')


@router.post('/cand', response_model=list[AddressChoice], response_class=JSONResponse)
async def get_addr_choices(
    # postcode: VALID_POSTCODE,
    postcode: VALID_POSTCODE = Body(...),
    address: AddressBase = Body(None),
    el_client: ELClient = Depends(get_el_client),
) -> list[AddressChoice]:
    """Fetch candidate address choices for a postcode, optionally scored by closeness to provided address.

    Args:
        postcode: VALID_POSTCODE - postcode to search for
        address: AddressBase - address to compare to candidates
        el_client: ELClient - Parcelforce ExpressLink client
    """
    logger.warning(f'Fetching candidates for {postcode=}, {address=}')
    res = el_client.get_choices(postcode=postcode, address=address)
    return res


@router.post('/post_ship', response_class=HTMLResponse)
async def post_form(
    request: Request,
    shipment: AmherstShipment = Depends(shipment_f_form),
    record_str: str = Form(...),
):
    logger.info('Shipment Form Posted')
    return TEMPLATES.TemplateResponse(
        'ship/order_review.html',
        {'request': request, 'shipment': shipment, 'record_str': record_str},
    )


@router.post('/post_confirm', response_class=HTMLResponse)
async def post_confirm_booking(
    request: Request,
    shipment: AmherstShipment = Depends(shipment_str_form_to_shipment),
    record: AmherstTableBase = Depends(record_from_json_str_form),
    el_client: ELClient = Depends(get_el_client),
    record_str: str = Form(...),
):
    # todo update commence
    # record = await record_str_to_record(record_str)

    logger.info('Confirming booking')
    shipment_response: ShipmentResponse = book_shipment(el_client, shipment)
    if not shipment_response.success:
        alerts = jsonable_encoder(shipment_response.alerts)
        return TEMPLATES.TemplateResponse(
            'alerts.html', {'request': request, 'alerts': alerts, 'shipment': shipment, 'record_str': record_str}
        )
    if shipment.direction == 'out' or shipment.print_own_label:
        wait_label(shipment_num=shipment_response.shipment_num, dl_path=shipment.label_file, el_client=el_client)
    logger.info(f'Booked Shipment Response: {shipment_response}')
    return TEMPLATES.TemplateResponse(
        'ship/order_confirmed.html', {'request': request, 'shipment': shipment, 'response': shipment_response}
    )
