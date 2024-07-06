from fastapi import APIRouter, Depends
from loguru import logger
from starlette.responses import JSONResponse

from amherst.shipment_funcs import book_shipment, shipment_request_f_form
from amherst.route_depends import (
    SearchResponse,
    get_el_client,
    search_body,
    search_body_more,
    search_query,
    search_query_more,
)
from amherst.models.am_record_smpl import AMHERST_TABLE_TYPES
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressChoice
from shipaw.models.pf_msg import ShipmentResponse
from shipaw.models.pf_shipment import Shipment, ShipmentAwayCollection
from shipaw.ship_types import VALID_POSTCODE

TABLE_LIST_More = tuple[list[AMHERST_TABLE_TYPES], bool]
router = APIRouter()


@router.get('/searchmore', response_class=JSONResponse)
async def search_query_more[T: AMHERST_TABLE_TYPES](
        response: SearchResponse = Depends(search_query_more),
) -> SearchResponse[T]:
    return response


@router.post('/searchmore')
async def search_body_more[T: AMHERST_TABLE_TYPES](
        response: SearchResponse = Depends(search_body_more),
) -> SearchResponse[T]:
    return response


@router.get('/search')
async def search_query[T: AMHERST_TABLE_TYPES](
        amrecs: list[T] = Depends(search_query),
) -> list[T]:
    logger.info(T)
    for amrec in amrecs:
        logger.info(f'{amrec.name=} {type(amrec)=}')
    return amrecs


@router.post('/search')
async def search_post[T: AMHERST_TABLE_TYPES](
        amrecs: list[T] = Depends(search_body),
) -> list[T]:
    return amrecs


@router.post('/form_to_ship/')
async def form_to_shipment(
        shipment_request: Shipment = Depends(shipment_request_f_form),
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
        shipment_request: Shipment = Depends(shipment_request_f_form),
) -> Shipment:
    logger.info(shipment_request.recipient_contact.notifications)
    return shipment_request


@router.post('/confirm_booking', response_class=JSONResponse)
async def confirm_booking(
        shipment: Shipment,
        el_client: ELClient = Depends(get_el_client),
) -> ShipmentResponse:
    if isinstance(shipment, ShipmentAwayCollection):
        logger.info(f'Collection from {shipment.collection_info.collection_address.address_line1}')
    return book_shipment(el_client, shipment)
