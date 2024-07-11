from fastapi import APIRouter, Depends

from amherst.back.route_depends import SearchRequest, SearchResponse
from amherst.back.pyc_backend import pycommence_response, row_from_path
from amherst.models.amherst_models import AMHERST_TABLE_TYPES

router = APIRouter()


@router.get('/{csrname}/search/{pk_value}')
async def search_get[T: SearchResponse](
        search_request: SearchRequest = Depends(SearchRequest.srch_from_path),
) -> T:
    return await pycommence_response(search_request)


@router.get('/{csrname}/{row_id}')
async def get_row(
        row: dict = Depends(row_from_path),
) -> AMHERST_TABLE_TYPES:
    return row


@router.post('/search')
async def search_post[T: SearchResponse](
        search_request: SearchRequest = Depends(SearchRequest.from_body),
) -> T:
    return await pycommence_response(search_request)


@router.get('/{csrname}')
async def get_all(
        search_request: SearchRequest = Depends(SearchRequest.from_path),
) -> SearchResponse:
    return await pycommence_response(search_request)
