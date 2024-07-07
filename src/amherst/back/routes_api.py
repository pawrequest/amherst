from fastapi import APIRouter, Depends

from amherst.back.route_depends import SearchRequest, SearchResponse
from amherst.back.pyc_backend import pycommence_response
from amherst.models.amherst_models import AMHERST_TABLE_TYPES

TABLE_LIST_More = tuple[list[AMHERST_TABLE_TYPES], bool]
router = APIRouter()


@router.get('/search')
async def search_get[T: SearchResponse](
        search_request: SearchRequest = Depends(SearchRequest.from_query),
) -> T:
    resp = await pycommence_response(search_request)
    return resp


@router.post('/search')
async def search_post[T: SearchResponse](
        search_request: SearchRequest = Depends(SearchRequest.from_body),
) -> T:
    resp = await pycommence_response(search_request)
    return resp
