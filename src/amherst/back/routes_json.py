from fastapi import APIRouter, Depends

from amherst.back.backend_search_paginate import SearchResponse
from amherst.back.backend_pycommence import pycommence_response

router = APIRouter()


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
