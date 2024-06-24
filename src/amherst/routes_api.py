from fastapi import APIRouter, Depends
from loguru import logger
from starlette.responses import JSONResponse

from amherst.backend_funcs import book_shipment, booking_f_path, shipment_request_f_form
from amherst.db import get_el_client
from amherst.models.db_models import BookingStateDB
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressChoice
from shipaw.models.pf_msg import ShipmentResponse
from shipaw.models.pf_shipment import Shipment, ShipmentAwayCollection, ShipmentAwayDropoff
from shipaw.ship_types import VALID_POSTCODE

router = APIRouter()


@router.get('/ping', response_class=JSONResponse)
async def ping():
    return {'ping': 'pong'}


@router.get('/candidates', response_model=list[AddressChoice], response_class=JSONResponse)
async def fetch_candidates(
    postcode: VALID_POSTCODE,
    el_client: ELClient = Depends(get_el_client),
):
    res = el_client.get_choices(postcode)
    return res


@router.post('/shiprec', response_class=JSONResponse)
async def shiprec_post(
    shipment_request: Shipment = Depends(shipment_request_f_form),
) -> Shipment:
    logger.info(shipment_request.notifications_str)
    return shipment_request


@router.post('/confirm_outbound', response_class=JSONResponse)
async def confirm_outbound(
    shipment: Shipment,
    el_client: ELClient = Depends(get_el_client),
) -> ShipmentResponse:
    logger.info(shipment.notifications_str)
    if isinstance(shipment, ShipmentAwayCollection):
        logger.info(f'Collection from {shipment.collection_info.collection_address.address_line1}')

    return book_shipment(el_client, shipment)


@router.post('/confirm_away_collect', response_class=JSONResponse)
async def confirm_away_collect(
    shipment: ShipmentAwayCollection,
    el_client: ELClient = Depends(get_el_client),
) -> ShipmentResponse:
    logger.info(shipment.notifications_str)
    logger.info(f'Collection from {shipment.collection_info.collection_address.address_line1}')
    return book_shipment(el_client, shipment)


@router.post('/confirm_away_dropoff', response_class=JSONResponse)
async def confirm_away_dropoff(
    shipment: ShipmentAwayDropoff,
    el_client: ELClient = Depends(get_el_client),
) -> ShipmentResponse:
    logger.info(shipment.notifications_str)
    logger.info(shipment.sender_contact.contact_name)
    return book_shipment(el_client, shipment)


@router.get('/{booking_id}', response_class=JSONResponse)
async def fetch_booking(
    booking: BookingStateDB = Depends(booking_f_path),
) -> BookingStateDB:
    return booking
