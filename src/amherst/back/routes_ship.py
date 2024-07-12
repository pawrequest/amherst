from fastapi import APIRouter, Body, Depends
from loguru import logger
from starlette.requests import Request
from starlette.responses import JSONResponse

from amherst.actions.shipper import book_shipment, get_el_client, shipment_request_f_form
from amherst.back.pyc_backend import row_from_path
from amherst.config import TEMPLATES
from amherst.models.amherst_models import AMHERST_TABLE_TYPES
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressChoice
from shipaw.models.pf_msg import ShipmentResponse
from shipaw.models.pf_shipment import ShipmentAwayCollectionConfigured, ShipmentConfigured
from shipaw.ship_types import VALID_POSTCODE

router = APIRouter()


@router.get('/form')
async def shipping_form(request: Request):
    return TEMPLATES.TemplateResponse('shipping_form.html', {'request': request})


@router.get('/{csrname}/{row_id}')
async def shipping_form_post(
        request: Request,
        row: AMHERST_TABLE_TYPES = Depends(row_from_path),
):
    shipment_request = row.shipment_dict()
    return TEMPLATES.TemplateResponse('shipping_form.html', {'request': request, 'shipment': shipment_request})


@router.post('/form_to_ship/')
async def form_to_shipment(
        shipment_request: ShipmentConfigured = Depends(shipment_request_f_form),
):
    return shipment_request


@router.get('/candidates', response_model=list[AddressChoice], response_class=JSONResponse)
async def fetch_candidates(
        postcode: VALID_POSTCODE,
        el_client: ELClient = Depends(get_el_client),
):
    res = el_client.get_choices(postcode)
    return res


@router.post('/shiprec', response_class=JSONResponse)
async def shiprec_post(
        shipment_request: ShipmentConfigured = Depends(shipment_request_f_form),
) -> ShipmentConfigured:
    logger.info(shipment_request.recipient_contact.notifications)
    return shipment_request


@router.post('/confirm_booking', response_class=JSONResponse)
async def confirm_booking(
        shipment: ShipmentConfigured,
        el_client: ELClient = Depends(get_el_client),
) -> ShipmentResponse:
    if isinstance(shipment, ShipmentAwayCollectionConfigured):
        logger.info(f'Collection from {shipment.collection_info.collection_address.address_line1}')
    return book_shipment(el_client, shipment)
