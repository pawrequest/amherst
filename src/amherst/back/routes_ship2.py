from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse

from shipaw.expresslink_client import ELClient
from shipaw.models.pf_msg import ShipmentResponse
from amherst.back.backend_shipper import (
    amherst_shipment_str_to_shipment,
    book_shipment,
    get_el_client,
    shipment_f_form2, wait_label,
)
from amherst.back.backend_pycommence import get_one
from amherst.config import TEMPLATES
from amherst.models.amherst_models import (
    AMHERST_TABLE_MODELS,
    AmherstShipment,
    AmherstShipmentResponse,
)

router = APIRouter()


@router.get('/form2', response_class=HTMLResponse)
async def ship_form_extends_p2(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(get_one),
):
    logger.debug(f'Ship Form shape: {record.row_id=}')
    template = 'ship/form_shape2.html'
    return TEMPLATES.TemplateResponse(template, {'request': request, 'record': record})


@router.get('/form_content2', response_class=HTMLResponse)
async def ship_form_content2(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(get_one),
):
    logger.debug(f'Ship Form Content: {record.row_id}')
    template = 'ship/form_content2.html'
    return TEMPLATES.TemplateResponse(template, {'request': request, 'record': record})


@router.post('/post_ship2', response_class=HTMLResponse)
async def post_form2(
    request: Request,
    shipment_proposed: AmherstShipment = Depends(shipment_f_form2),
):
    logger.info('Shipment Form Posted')
    template = 'ship/order_review2.html'
    return TEMPLATES.TemplateResponse(
        template, {'request': request, 'shipment_proposed': shipment_proposed}
    )


@router.post('/post_confirm2', response_class=HTMLResponse)
async def post_confirm_booking2(
    request: Request,
    shipment_proposed: AmherstShipment = Depends(amherst_shipment_str_to_shipment),
    el_client: ELClient = Depends(get_el_client),
):
    logger.info('Booking Shipent')
    shipment_response: ShipmentResponse = book_shipment(el_client, shipment_proposed.shipment())
    amherst_ship_response: AmherstShipmentResponse = AmherstShipmentResponse(
        row_id=shipment_proposed.row_id, category=shipment_proposed.category, **shipment_response.model_dump()
    )
    logger.info(f'Booked AmherstShipment Response: {amherst_ship_response}')

    if not amherst_ship_response.success:
        alerts = jsonable_encoder(amherst_ship_response.alerts)
        return TEMPLATES.TemplateResponse(
            'alerts.html',
            {'request': request, 'alerts': alerts, 'shipment_proposed': shipment_proposed},
        )
    if shipment_proposed.direction == 'out' or shipment_proposed.print_own_label:
        wait_label(
            shipment_num=amherst_ship_response.shipment_num, dl_path=shipment_proposed.label_file, el_client=el_client
        )

    return TEMPLATES.TemplateResponse(
        'ship/order_confirmed.html',
        {'request': request, 'shipment_confirmed': shipment_proposed, 'response': amherst_ship_response},
    )
