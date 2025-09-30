import flaskwebgui
from fastapi import APIRouter, Depends, Query
from loguru import logger
from pycommence import PyCommence
from starlette.requests import Request

from amherst.back.backend_pycommence import pycmc_f_query, pycommence_search
from amherst.back.backend_search_paginate import SearchResponse
from amherst.config import amherst_settings
from amherst.models.amherst_models import AmherstShipableBase
from amherst.models.commence_adaptors import CursorName
from amherst.models.meta import get_table_model

router = APIRouter()


@router.get('/fetch', response_model=AmherstShipableBase)
async def fetch(
    request: Request,
    pycmc: PyCommence = Depends(pycmc_f_query),
    csrname: CursorName = Query(..., description='Cursor name to fetch record from'),
    row_id: str = Query(None, description='Row ID of the record to fetch'),
    pk_value: str = Query(None, description='Primary key value of the record to fetch'),
) -> AmherstShipableBase:
    """Fetch a record from the specified cursor name."""
    if not csrname or not any([row_id, pk_value]):
        raise ValueError('CsrName and Either row_id or pk_value must be provided')
    if not row_id:
        row_id = pycmc.csr(csrname).pk_to_id(pk_value)
    record = pycmc.read_row(csrname=csrname, row_id=row_id)
    model_type = get_table_model(csrname)
    return model_type.model_validate(record)


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
    return amherst_settings().templates.TemplateResponse('testing.html', {'request': request})


@router.get('/')
async def pycommence_search_endpoint(
    search_response: SearchResponse = Depends(pycommence_search),
) -> SearchResponse:
    return search_response


