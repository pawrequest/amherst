import os
from pathlib import Path

import pawdf
from fastapi import APIRouter, Depends, Query
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse

from amherst.back.backend_pycommence import gather_records_gen, pycmc_f_query, pycommence_context, pycommence_response
from amherst.back.backend_search_paginate import Pagination, SearchRequest, SearchResponse, SearchResponseMulti
from amherst.config import TEMPLATES
from amherst.models.amherst_models import AMHERST_ORDER_MODELS
from amherst.models.commence_adaptors import AmherstTableName
from amherst.models.maps import AmherstMapping, mapper_csrname
from pycommence.filters import ConditionType
from pycommence.pycommence_v2 import PyCommence

router = APIRouter()


@router.get('/open-file', response_class=HTMLResponse)
async def open_file(request: Request, filepath: str = Query(...)):
    os.startfile(filepath)
    return HTMLResponse(content=f'<p>Opened {filepath}</p>')


@router.post('/print-file', response_class=HTMLResponse)
async def print_file(request: Request, filepath: str = Query(...)):
    pawdf.array_pdf.convert_many(Path(filepath), print_files=True)
    return HTMLResponse(content=f'<p>Printed {filepath}</p>')


@router.get('/search')
async def search(
    request: Request,
    pycmc: PyCommence = Depends(pycmc_f_query),
    search_request: SearchRequest = Depends(SearchRequest.from_query),
    mapper: AmherstMapping = Depends(mapper_csrname),
):
    search_response: SearchResponse = await pycommence_response(search_request, pycmc, mapper=mapper)
    logger.debug(str(search_response))
    return TEMPLATES.TemplateResponse(mapper.listing_template, {'request': request, 'response': search_response})


# @router.get('/fetch')
# async def fetch(
#     request: Request,
#     record=Depends(get_one),
#     template_name: str = Depends(listing_template_name_q),
# ):
#     logger.info(str(record))
#     return TEMPLATES.TemplateResponse(template_name, {'request': request, 'record': record})


# @router.get('/search-f')
# async def search_f(
#     request: Request,
#     pycmc: PyCommence = Depends(pycmc_f_query2),
#     # pycmc: PyCommence = Depends(pycmc_f_query),
#     search_request: SearchRequest = Depends(SearchRequest.from_query),
#     template_name: str = Depends(listing_template_name_q),
# ):
#     search_response: SearchResponse = await pycommence_response(search_request, pycmc)
#     logger.info(f'Search Returned {search_response.length} {search_response.search_request.csrname} records')
#     return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': search_response})


@router.get('/customer')
async def customer(
    request: Request,
    customer_name: str = Query(''),
    customer_id: str = Query(''),
    filtered: bool = Query(False),
    py_filter: bool = Query(False),
    pagination: Pagination | None = Depends(Pagination.from_query),
):
    if not any([customer_id, customer_name]):
        return HTMLResponse(content='<p>Invalid Customer Name or ID</p>')
    template_name: str = 'hires_sales.html'

    hire_request = SearchRequest(
        csrname=AmherstTableName.Hire,
        condition=ConditionType.EQUAL,
        filtered=filtered,
        py_filter=py_filter,
        pagination=pagination,
    )
    sale_request = SearchRequest(
        csrname=AmherstTableName.Sale,
        condition=ConditionType.EQUAL,
        filtered=filtered,
        py_filter=py_filter,
        pagination=pagination,
    )

    if customer_id:
        raise NotImplementedError('Customer ID not implemented')
        # hire_request.row_id = sale_request.row_id = customer_id
    elif customer_name:
        hire_request.customer_name = sale_request.customer_name = customer_name

    # logger.warning(f'HireRequest: {str(hire_request)}')

    with pycommence_context(AmherstTableName.Hire) as pycmc:
        # todo filter_array
        hires, more_hires = await gather_records_gen(pycmc, hire_request)

    with pycommence_context(AmherstTableName.Sale) as pycmc:
        sales, more_sales = await gather_records_gen(pycmc, sale_request)

    records: list[AMHERST_ORDER_MODELS] = hires + sales
    records.sort(key=lambda x: x.send_date, reverse=True)
    response = SearchResponseMulti(records=records, search_request=[hire_request, sale_request])
    logger.debug(str(response))
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})
