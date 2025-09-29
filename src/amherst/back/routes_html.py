import os

from fastapi import APIRouter, Depends, Query
from loguru import logger
from pycommence import PyCommence, pycommence_context
from starlette.requests import Request
from starlette.responses import HTMLResponse

from amherst.back.backend_pycommence import pycmc_f_query, pycommence_gather, pycommence_search
from amherst.back.backend_search_paginate import (
    SearchRequest,
    SearchResponse,
    SearchResponseMulti,
)
from amherst.config import amherst_settings
from amherst.models.amherst_models import AMHERST_ORDER_MODELS
from amherst.models.maps import AmherstMap, mapper_from_query_csrname

router = APIRouter()


@router.get('/open-file', response_class=HTMLResponse)
async def open_file(filepath: str = Query(...)):
    os.startfile(filepath)
    return HTMLResponse(content=f'<span>Re</span>')


@router.post('/print-file', response_class=HTMLResponse)
async def print_file(filepath: str = Query(...)):
    os.startfile(filepath, 'print')
    return HTMLResponse(content=f'<span>Re</span>')


@router.get('/search')
async def search(
    request: Request,
    pycmc: PyCommence = Depends(pycmc_f_query),
    search_request: SearchRequest = Depends(SearchRequest.from_query),
    mapper: AmherstMap = Depends(mapper_from_query_csrname),
):
    search_response: SearchResponse = await pycommence_search(search_request, pycmc)
    logger.debug(str(search_response))
    return amherst_settings().templates.TemplateResponse(mapper.templates.listing, {'request': request, 'response': search_response})


@router.get('/orders')
async def orders(
    request: Request,
    q: SearchRequest = Depends(SearchRequest.from_query),
):
    template_name: str = 'order_list.html'
    requests = []
    for csrname in q.csrnames:
        logger.warning('pagination maybe sketchy for multiple categories?')
        if q.customer_name:
            q.customer_names.append(q.customer_name)
        for customer in q.customer_names:
            requests.append(
                SearchRequest(
                    csrname=csrname,
                    condition=q.condition,
                    py_filter_i=q.py_filter_i,
                    cmc_filter_i=q.cmc_filter_i,
                    pagination=q.pagination,
                    customer_name=customer,
                )
            )
    records: list[AMHERST_ORDER_MODELS] = []
    for req in requests:
        with pycommence_context(req.csrname) as pycmc:
            res, more = await pycommence_gather(pycmc, req)
            records.extend(res)

    records.sort(key=lambda x: x.send_date, reverse=True)
    response = SearchResponseMulti(records=records, search_request=requests)
    logger.debug(str(response))
    return amherst_settings().templates.TemplateResponse(template_name, {'request': request, 'response': response})

