import flaskwebgui
from fastapi import APIRouter, Depends, Query
from loguru import logger
from pycommence import PyCommence
from starlette.requests import Request

from amherst.back.backend_search_paginate import SearchResponse
from amherst.back.backend_pycommence import pycmc_f_query, pycommence_search
from amherst.config import TEMPLATES
from amherst.models.amherst_models import AMHERST_TABLE_MODELS

router = APIRouter()

@router.get('/fetch', response_model=AMHERST_TABLE_MODELS)
async def fetch(
    request: Request,
    pycmc: PyCommence = Depends(pycmc_f_query),
    csrname: str = Query(..., description='Cursor name to fetch record from'),
    row_id: str = Query(None, description='Row ID of the record to fetch'),
    pk_value: str = Query(None, description='Primary key value of the record to fetch'),
) -> AMHERST_TABLE_MODELS:
    """Fetch a record from the specified cursor name."""
    if not csrname or not any([row_id, pk_value]):
        raise ValueError('CsrName and Either row_id or pk_value must be provided')
    if not row_id:
        row_id = pycmc.csr(csrname).pk_to_id(pk_value)
    record = pycmc.read_row(csrname=csrname, row_id=row_id)
    return record

@router.get('/close_app/', response_model=None, response_model_exclude_none=True)
async def close_app():
    """Endpoint to close the application."""
    logger.warning('Closing application')
    flaskwebgui.close_application()


@router.get('/health/', response_model=str)
async def health():
    return 'healthy'


@router.get('/testing/', response_model=str)
async def testing(
    request: Request,
):
    return TEMPLATES.TemplateResponse('testing.html', {'request': request})


# @router.post('/')
# async def post2(
#     search_response: SearchResponse2 = Depends(pycommence_response2),
# ) -> SearchResponse2:
#     return search_response


@router.get('/')
async def get_new(
    search_response: SearchResponse = Depends(pycommence_search),
) -> SearchResponse:
    return search_response


#
# @router.post('/cand', response_model=list[AddressChoice], response_class=JSONResponse)
# async def get_addr_choices(
#     postcode: VALID_POSTCODE = Body(...),
#     address: AddressBase = Body(None),
#     el_client: ELClient = Depends(get_el_client),
# ) -> list[AddressChoice]:
#     """Fetch candidate address choices for a postcode, optionally scored by closeness to provided address.
#
#     Args:
#         postcode: VALID_POSTCODE - postcode to search for
#         address: AddressBase - address to compare to candidates
#     """
#     logger.warning(f'Fetching candidates for {postcode=}, {address=}')
#     res = el_client.get_choices(postcode=postcode, address=address)
#     return res


# @router.post('/cand2', response_model=list[AddressChoice], response_class=JSONResponse)
# async def fetch_cand2(
#     postcode: VALID_POSTCODE = Query(...),
#     address_str: str = Body(...),
#     el_client: ELClient = Depends(get_el_client),
# ):
#     address = add_from_str(add_str=address_str, postcode=postcode)
#     res = el_client.get_choices(postcode=postcode, address=address)
#     return res


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
