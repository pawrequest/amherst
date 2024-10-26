from fastapi import APIRouter, Depends

from amherst.back.search_paginate import SearchRequest, SearchResponse
from amherst.back.backend_pycommence import pycommence_response, row_from_path_id
from amherst.models.amherst_models import AMHERST_TABLE_MODELS

router = APIRouter()


@router.get('/{csrname}/search/{pk_value}')
async def search_pk(
        search_request: SearchRequest = Depends(SearchRequest.from_path),
) -> SearchResponse:
    return await pycommence_response(search_request)


@router.get('/{csrname}/{row_id}')
async def get_row(
        row: AMHERST_TABLE_MODELS = Depends(row_from_path_id),
) -> AMHERST_TABLE_MODELS:
    return row


@router.post('/search')
async def search_post(
        search_request: SearchRequest = Depends(SearchRequest.from_body),
) -> SearchResponse:
    return await pycommence_response(search_request)


@router.get('/{csrname}')
async def get_all(
        search_request: SearchRequest = Depends(SearchRequest.get_all),
) -> SearchResponse:
    return await pycommence_response(search_request)
