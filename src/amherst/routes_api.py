from fastapi import APIRouter, Depends
from loguru import logger
from sqlmodel import Session, select
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse

from amherst.backend_funcs import amrec_from_path, book_shipment, shipment_request_f_form
from amherst.db import (
    Pagination,
    get_el_client,
    get_session,
    select_page_more,
    query_multi,
    amrecs_from_query,
)
from amherst.models.am_record_smpl import AmherstTableDB
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressChoice
from shipaw.models.pf_msg import ShipmentResponse
from shipaw.models.pf_shipment import Shipment, ShipmentAwayCollection
from shipaw.ship_types import ShipDirection, VALID_POSTCODE

router = APIRouter()


@router.get('/multi_search', response_model=list[AmherstTableDB])
async def multi_search(
        stmt: select = Depends(query_multi),
        session: Session = Depends(get_session),
        pagination: Pagination = Depends(Pagination.from_query),
) -> list[AmherstTableDB]:
    page, more = await select_page_more(session, stmt, pagination)
    if not page:
        raise HTTPException(status_code=404, detail='No records found')
    return page


@router.get('/search', response_model=list[AmherstTableDB])
async def search(
        page: list[AmherstTableDB] = Depends(amrecs_from_query),
) -> list[AmherstTableDB]:
    return page


#
# @router.get('/search2', response_model=list[AmherstTableDB])
# async def search2(
#         column: str | None = Query(None),
#         q: str | None = Query(None),
#         session: Session = Depends(get_session),
#         pagination: Pagination = Depends(get_pagination)
# ) -> list[AmherstTableDB]:
#     stmt = search_column_stmt(AmherstTableDB, column, q)
#     page, more = await select_page_more(session, stmt, pagination)
#     if not page:
#         raise HTTPException(status_code=404, detail=f'No records found for {q}')
#     return page


#
# @router.get('/search2', response_model=list[AmherstTableDB])
# async def search2(
#         column: str | None = Query(None),
#         search_str: str | None = Query(None),
#         session: Session = Depends(get_session)
# ) -> list[AmherstTableDB]:
#     stmt = search_column_stmt(AmherstTableDB, column, search_str)
#     res = session.exec(stmt).all()
#     if not res:
#         stmt = search_column_stmt(AmherstTableDB, 'name', search_str)
#         res = session.exec(stmt).all()
#     if not res:
#         raise ValueError(f'No records found for {search_str}')
#     return res[:10]
#

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
