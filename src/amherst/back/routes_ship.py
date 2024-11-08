from fastapi import APIRouter, Body, Depends, Form
from fastapi.encoders import jsonable_encoder
from loguru import logger
from shipaw.models.pf_shipment import Shipment
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
    record_from_form,
    shipment_f_form,
    shipment_str_form_to_shipment,
    wait_label,
)
from amherst.back.backend_pycommence import get_one
from amherst.config import TEMPLATES
from amherst.models.amherst_models import AMHERST_TABLE_MODELS, AmherstTableBase

router = APIRouter()


async def jsonable_s_r(record: AmherstTableBase, shipment: Shipment | None = None) -> tuple[Shipment, dict]:
    shipment = shipment or record.shipment_pyd()
    shipment = jsonable_encoder(shipment)
    record = jsonable_encoder(record)
    return shipment, record


async def templated_ship_record(template: str, request: Request, record: AmherstTableBase, shipment: Shipment = None):
    shipment, record = await jsonable_s_r(record, shipment)
    return TEMPLATES.TemplateResponse(template, {'request': request, 'shipment': shipment, 'record': record})



@router.get('/form-p', response_class=HTMLResponse)
async def ship_form_extends_p(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(get_one),
    # SearchRequest
):
    logger.debug(f'PYDANTIC Ship Form extends, {record.row_id=}')
    template = 'ship/form_shape.html'
    shipment: Shipment = record.shipment_pyd()
    return TEMPLATES.TemplateResponse(template, {'request': request, 'shipment': shipment, 'record': record})


@router.get('/form_content', response_class=HTMLResponse)
async def ship_form_content(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(get_one),
):
    logger.debug(f'SHIP FROM ROW ID: {record.row_id}')
    template = 'ship/form_content.html'
    shipment: Shipment = record.shipment_pyd()
    return TEMPLATES.TemplateResponse(template, {'request': request, 'shipment': shipment, 'record': record})

    # return await templated_ship_record(template, request, record)


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
    logger.debug(f'Fetching candidates for {postcode=}, {address=}')
    res = el_client.get_choices(postcode=postcode, address=address)
    return res


@router.post('/post_ship', response_class=HTMLResponse)
async def post_form(
    request: Request,
    # record: dict,
    shipment: Shipment = Depends(shipment_f_form),
    record=Depends(record_from_form),
):
    logger.info('Shipment Form Posted')
    template = 'ship/order_review.html'
    return TEMPLATES.TemplateResponse(template, {'request': request, 'shipment': shipment, 'record': record})


@router.post('/post_confirm', response_class=HTMLResponse)
async def post_confirm_booking(
    request: Request,
    shipment: Shipment = Depends(shipment_str_form_to_shipment),
    record: AmherstTableBase = Depends(record_from_json_str_form),
    el_client: ELClient = Depends(get_el_client),
    ship2: str = Form(''),
):
    logger.info('Booking Shipent')
    shipment_response: ShipmentResponse = book_shipment(el_client, shipment)
    logger.info(f'Booked Shipment Response: {shipment_response}')

    if not shipment_response.success:
        alerts = jsonable_encoder(shipment_response.alerts)
        return TEMPLATES.TemplateResponse(
            'alerts.html', {'request': request, 'alerts': alerts, 'shipment': shipment, 'record': record}
        )
    if shipment.direction == 'out' or shipment.print_own_label:
        wait_label(shipment_num=shipment_response.shipment_num, dl_path=shipment.label_file, el_client=el_client)

    return TEMPLATES.TemplateResponse(
        'ship/order_confirmed.html',
        {'request': request, 'shipment': shipment, 'response': shipment_response, 'record': record},
    )
