from fastapi import APIRouter, Depends
from loguru import logger
from starlette.responses import JSONResponse

from amherst.backend_funcs import book_shipment, booking_f_path, shipment_request_f_form
from amherst.db import get_el_client
from amherst.models.db_models import BookingStateDB
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressChoice
from shipaw.models.pf_msg import ShipmentResponse
from shipaw.models.pf_shipment import Shipment
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
    return shipment_request


@router.post('/confirm_booking', response_class=JSONResponse)
async def confirm_api(
    shipment_request: Shipment,
    el_client: ELClient = Depends(get_el_client),
) -> ShipmentResponse:
    msg = f'Confirming booking to {shipment_request.recipient_address.address_line1}'
    msg = (
        f'{msg}\n'
        f'Recip Notifications = {shipment_request.recipient_contact.email_address}'
        f' + {shipment_request.recipient_contact.mobile_phone} '
        f'{shipment_request.recipient_contact.notifications}\n'
    )
    if shipment_request.collection_info:
        msg += (
            f'Collection Notifications = {shipment_request.collection_info.collection_contact.email_address} '
            f'+ {shipment_request.collection_info.collection_contact.mobile_phone}'
        )

    logger.info(msg)
    if shipment_request.collection_info:
        logger.info(f'Collection from {shipment_request.collection_info.collection_address.address_line1}')

    return book_shipment(el_client, shipment_request)


@router.get('/{booking_id}', response_class=JSONResponse)
async def fetch_booking(
    booking: BookingStateDB = Depends(booking_f_path),
) -> BookingStateDB:
    return booking
