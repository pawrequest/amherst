from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from amherst.backend_funcs import book_shipment, booking_f_path, shipment_request_f_form
from amherst.db import get_el_client
from amherst.models.db_models import BookingStateDB
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressChoice
from shipaw.models.pf_msg import CreateShipmentResponse
from shipaw.models.pf_shipment import ShipmentRequest
from shipaw.ship_types import VALID_POSTCODE

router = APIRouter()


@router.get('/candidates', response_model=list[AddressChoice], response_class=JSONResponse)
async def fetch_candidates(
    postcode: VALID_POSTCODE,
    el_client: ELClient = Depends(get_el_client),
):
    res = el_client.get_choices(postcode)
    return res


@router.get('/{booking_id}', response_class=JSONResponse)
async def fetch_booking(
    booking: BookingStateDB = Depends(booking_f_path),
) -> BookingStateDB:
    return booking


@router.post('shiprec', response_class=JSONResponse)
async def shiprec_api(
    shipment_request: ShipmentRequest = Depends(shipment_request_f_form),
) -> ShipmentRequest:
    return shipment_request


@router.post('/confirm_booking', response_class=JSONResponse)
async def confirm_api(
    shipment_request: ShipmentRequest,
    el_client: ELClient = Depends(get_el_client),
) -> CreateShipmentResponse:
    response = book_shipment(el_client, shipment_request)
    return response
