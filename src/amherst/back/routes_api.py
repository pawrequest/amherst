from fastapi import APIRouter, Depends

from amherst.back.route_depends import search_get, search_post
from amherst.back.route_depends_types import SearchResponse
from amherst.models.amherst_models import AMHERST_TABLE_TYPES

TABLE_LIST_More = tuple[list[AMHERST_TABLE_TYPES], bool]
router = APIRouter()


@router.get('/search')
async def search_get[T: SearchResponse](
        response: T = Depends(search_get),
) -> T:
    return response


@router.post('/search')
async def search_post[T: SearchResponse](
        response: SearchResponse = Depends(search_post),
) -> T:
    return response
