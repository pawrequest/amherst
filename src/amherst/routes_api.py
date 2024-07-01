from fastapi import APIRouter, Depends
from loguru import logger
from sqlmodel import col, select
from starlette.responses import JSONResponse

from amherst.backend_funcs import amrec_from_path, book_shipment, shipment_request_f_form
from amherst.db import get_el_client, get_session
from amherst.models.am_record_smpl import AmherstTableDB
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressChoice
from shipaw.models.pf_msg import ShipmentResponse
from shipaw.models.pf_shipment import Shipment, ShipmentAwayCollection
from shipaw.ship_types import ShipDirection, VALID_POSTCODE

router = APIRouter()


@router.get('/search/{column}/{search_str}', response_model=list[AmherstTableDB])
async def search(column: str, search_str: str, session=Depends(get_session)) -> list[AmherstTableDB]:
    search_ = f'%{search_str}%'
    colly = getattr(AmherstTableDB, column)
    stmt = select(AmherstTableDB).where(col(colly).ilike(search_))
    res = session.exec(stmt).all()
    return res


@router.post('/form_to_ship/', response_model=Shipment)
async def form_to_shipment(
        shipment_request: Shipment = Depends(shipment_request_f_form),
):
    return shipment_request


@router.get('/get_shipment/{direction}/{row_id}', response_model=Shipment)
async def fetch_amrec_shipment(direction: ShipDirection, amrec: AmherstTableDB = Depends(amrec_from_path)):
    return amrec.to_shipment(direction)


@router.get('/get_amrec/{row_id}', response_model=AmherstTableDB)
async def fetch_amrec(amrec: AmherstTableDB = Depends(amrec_from_path)):
    return amrec


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
