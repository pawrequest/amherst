import os
from pathlib import Path

import pawdf
from fastapi import APIRouter, Depends, Query
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse

from amherst.back.backend_pycommence import gather_records_q, pycmc_f_query, pycommence_context, pycommence_response
from amherst.back.backend_search_paginate import SearchRequest, SearchResponse, SearchResponseMulti
from amherst.config import TEMPLATES
from amherst.models.amherst_models import AMHERST_ORDER_MODELS
from amherst.models.commence_adaptors import AmherstTableName
from amherst.models.maps import listing_template_name_q
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
    template_name: str = Depends(listing_template_name_q),
):
    search_response: SearchResponse = await pycommence_response(search_request, pycmc)
    logger.info(str(search_response))
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': search_response})


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
):
    if not any([customer_id, customer_name]):
        return HTMLResponse(content='<p>Invalid Customer Name or ID</p>')
    template_name: str = 'hires_sales.html'

    hire_request = SearchRequest(csrname=AmherstTableName.Hire, condition=ConditionType.EQUAL, filtered=filtered)
    sale_request = SearchRequest(csrname=AmherstTableName.Sale, condition=ConditionType.EQUAL, filtered=filtered)

    if customer_id:
        raise NotImplementedError('Customer ID not implemented')
        # hire_request.row_id = sale_request.row_id = customer_id
    elif customer_name:
        hire_request.customer_name = sale_request.customer_name = customer_name

    with pycommence_context(AmherstTableName.Hire, filter_array=hire_request.filter_array()) as pycmc:
        hires, more_hires = await gather_records_q(pycmc, hire_request)
        # hires = filter_records(hires)

    with pycommence_context(AmherstTableName.Sale, filter_array=sale_request.filter_array()) as pycmc:
        sales, more_sales = await gather_records_q(pycmc, sale_request)
        # sales = filter_records(sales)

    records: list[AMHERST_ORDER_MODELS] = hires + sales
    records.sort(key=lambda x: x.send_date, reverse=True)
    response = SearchResponseMulti(records=records, search_request=[hire_request, sale_request])
    logger.info(str(response))
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})
