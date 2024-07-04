from fastapi import APIRouter, Depends
from loguru import logger
from starlette.responses import JSONResponse

from amherst.shipment_funcs import book_shipment, shipment_request_f_form
from amherst.db import (
    get_el_client,
    get_pyc2,
    get_them,
)
from amherst.models.am_record_smpl import AMHERST_TABLE_TYPES
from pycommence.pycommence_v2 import PyCommence
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressChoice
from shipaw.models.pf_msg import ShipmentResponse
from shipaw.models.pf_shipment import Shipment, ShipmentAwayCollection
from shipaw.ship_types import VALID_POSTCODE

TABLE_LIST_More = tuple[list[AMHERST_TABLE_TYPES], bool]
router = APIRouter()


@router.get('/pyc_pk/{csrname}/{pk_value}', response_class=JSONResponse)
async def getpyc(csrname: str, pk_value: str, pycmc: PyCommence = Depends(get_pyc2)) -> list[dict]:
    csr = pycmc.csr(csrname)
    return csr.read_rows_pk_contains(pk_value)


@router.post('/search/{category}', response_model=list[AMHERST_TABLE_TYPES])
async def search(
        res: TABLE_LIST_More = Depends(get_them),
) -> list[AMHERST_TABLE_TYPES]:
    page, more = res
    return page


@router.post('/form_to_ship/', response_model=Shipment)
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
