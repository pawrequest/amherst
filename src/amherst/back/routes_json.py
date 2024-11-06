from fastapi import APIRouter, Body, Depends
from loguru import logger
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressBase, AddressChoice
from shipaw.ship_types import VALID_POSTCODE
from starlette.responses import JSONResponse

from amherst.back.backend_search_paginate import SearchResponse
from amherst.back.backend_pycommence import pycommence_response
from amherst.back.backend_shipper import get_el_client

router = APIRouter()


@router.post('/cand', response_model=list[AddressChoice], response_class=JSONResponse)
async def get_addr_choices(
    postcode: VALID_POSTCODE = Body(...),
    address: AddressBase = Body(None),
    el_client: ELClient = Depends(get_el_client),
) -> list[AddressChoice]:
    """Fetch candidate address choices for a postcode, optionally scored by closeness to provided address.

    Args:
        postcode: VALID_POSTCODE - postcode to search for
        address: AddressBase - address to compare to candidates
    """
    logger.warning(f'Fetching candidates for {postcode=}, {address=}')
    res = el_client.get_choices(postcode=postcode, address=address)
    return res


# @router.post('/cand2', response_model=list[AddressChoice], response_class=JSONResponse)
# async def fetch_cand2(
#     postcode: VALID_POSTCODE = Query(...),
#     address_str: str = Body(...),
#     el_client: ELClient = Depends(get_el_client),
# ):
#     address = add_from_str(add_str=address_str, postcode=postcode)
#     res = el_client.get_choices(postcode=postcode, address=address)
#     return res


@router.get('/new/{csrname}')
async def get_new(
    search_response: SearchResponse = Depends(pycommence_response),
) -> SearchResponse:
    return search_response


# @router.get('/{csrname}/{row_id}')
# async def get_row(
#         row: AMHERST_TABLE_MODELS = Depends(row_from_path_id),
# ) -> AMHERST_TABLE_MODELS:
#     return row


# @router.post('/search')
# async def search_post(
#         # search_request: SearchRequest = Depends(SearchRequest.from_body),
#         resp: SearchResponse = Depends(pycommence_response),
# ) -> SearchResponse:
#     # return await pycommence_response(search_request)
#     return resp


# @router.get('/{csrname}')
# async def get_all(
#         # search_request: SearchRequest = Depends(SearchRequest.get_all),
#         resp: SearchResponse = Depends(pycommence_response),
# ) -> SearchResponse:
#     # return await pycommence_response(search_request)
#     return resp
