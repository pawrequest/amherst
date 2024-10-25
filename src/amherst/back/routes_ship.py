from fastapi import APIRouter, Depends, Form
from fastapi.encoders import jsonable_encoder
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressChoice
from shipaw.models.pf_shipment_configured import ShipmentConfigured
from shipaw.ship_types import VALID_POSTCODE

from amherst.back.backend_shipper import book_shipment, get_el_client, shipment_from_record, shipment_request_f_form
from amherst.back.backend_pycommence import row_from_path_id, search_f_path
from amherst.back.search_paginate import SearchResponse
from amherst.config import TEMPLATES
from amherst.models.amherst_models import AMHERST_TABLE_MODELS, AmherstTableBase

router = APIRouter()


# @router.get('/form', response_class=HTMLResponse)
# async def shipping_form(request: Request):
#     return TEMPLATES.TemplateResponse('ship/shipping_form_play.html', {'request': request})


@router.get('/row_id/{csrname}/{row_id}')
async def ship_from_row_id_path(
        request: Request,
        row: AMHERST_TABLE_MODELS = Depends(row_from_path_id),
):
    logger.warning(f'SHIP FROM ROW ID PATH Row: {row}')
    return await record_to_form(request, row)
    # shipment = await shipment_from_row(row)
    # return TEMPLATES.TemplateResponse(
    #     'shipping_form.html', {'request': request, 'shipment': shipment.model_dump_json()}
    # )


@router.get('/pk/{csrname}/{pk_value}', response_class=JSONResponse)
async def ship_form_pk_value_path(
        request: Request,
        resp: SearchResponse = Depends(search_f_path),
):
    if resp.length == 1 or resp.search_request.pk_value == 'Test':
        row = resp.records[0]
        return await record_to_form(request, row)
    else:
        return resp
        # show a list


async def record_to_form(request, record: AmherstTableBase):
    shipment = await shipment_from_record(record)
    jsonable = jsonable_encoder(shipment)
    html = TEMPLATES.TemplateResponse('ship/shipping_form_play.html', {'request': request, 'shipment': jsonable})
    return html
    # response.headers['HX-Trigger'] = 'hydrateShipment'


@router.get('/candidates', response_model=list[AddressChoice], response_class=JSONResponse)
async def fetch_candidates(
        postcode: VALID_POSTCODE,
        el_client: ELClient = Depends(get_el_client),
):
    res = el_client.get_choices(postcode)
    return res


@router.post('/post_ship', response_class=HTMLResponse)
async def post_review_form(
        request: Request,
        shipment_request: ShipmentConfigured = Depends(shipment_request_f_form),
):
    logger.info(shipment_request.recipient_contact.notifications)
    return TEMPLATES.TemplateResponse('ship/order_review.html', {'request': request, 'shipment': shipment_request})


@router.post('/confirm_booking', response_class=HTMLResponse)
async def post_confirm_booking(
        request: Request,
        shipment: str = Form(...),
        # shipment: ShipmentConfigured,
        el_client: ELClient = Depends(get_el_client),
):
    logger.info(f'Confirm booking: {shipment}')
    shipment: ShipmentConfigured = ShipmentConfigured.model_validate_json(shipment)
    response = book_shipment(el_client, shipment)
    logger.info(f'Booked Shipment Response: {response}')
    return TEMPLATES.TemplateResponse(
        'ship/order_confirmed.html', {'request': request, 'shipment': shipment, 'response': response}
    )

    # return response


@router.post('/dl_label', response_class=HTMLResponse)
async def dl_label(
        shipment_number: str = Form(...),
        el_client: ELClient = Depends(get_el_client),
):
    logger.info(f'Fetching label for Shipment Number: {shipment_number}')
    # label_path = el_client.settings.


def get_label_path(shipment: ShipmentConfigured, label_dir):
    logger.debug(f'Getting label path for {shipment.pf_label_filestem}')
    if shipment.direction != 'out':
        label_dir = label_dir / shipment.direction
    lpath = (label_dir / shipment.pf_label_filestem).with_suffix('.pdf')
    incremented = 2
    while lpath.exists():
        logger.warning(f'Label path {lpath} already exists')
        lpath = lpath.with_name(f'{lpath.stem}_{incremented}{lpath.suffix}')
        incremented += 1
    logger.debug(f'Using label path={lpath}')
    return lpath
