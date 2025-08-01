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
from amherst.config import TEMPLATES
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
    return TEMPLATES.TemplateResponse(mapper.templates.listing, {'request': request, 'response': search_response})


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
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})


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


# @router.get('/customer')
# async def customer(
#     request: Request,
#     customer_name: str = Query(''),
#     customer_id: str = Query(''),
#     py_filter: FilterVariant = Query(None),
#     cmc_filter: FilterVariant = Query('loose'),
#     pagination: Pagination | None = Depends(Pagination.from_query),
#     cats: list[CsrName] = None,
# ):
#     cats = cats or [CsrName.Hire, CsrName.Sale, CsrName.Trial]
#     template_name: str = 'order_list.html'
#
#     for cat in cats:
#         maping = await maps2(cat)
#         q = SearchRequest(
#             csrname=cat,
#             condition=ConditionType.EQUAL,
#             py_filter=py_filter,
#             cmc_filter=cmc_filter,
#             pagination=pagination,
#         )
#
#     if not any([customer_id, customer_name]):
#         return HTMLResponse(content='<p>Invalid Customer Name or ID</p>')
#
#     hire_request = SearchRequest(
#         csrname=CsrName.Hire,
#         condition=ConditionType.EQUAL,
#         py_filter=py_filter,
#         cmc_filter=cmc_filter,
#         pagination=pagination,
#     )
#     sale_request = SearchRequest(
#         csrname=CsrName.Sale,
#         condition=ConditionType.EQUAL,
#         py_filter=py_filter,
#         cmc_filter=cmc_filter,
#         pagination=pagination,
#     )
#
#     if customer_id:
#         raise NotImplementedError('Customer ID not implemented')
#         # hire_request.row_id = sale_request.row_id = customer_id
#     elif customer_name:
#         hire_request.customer_name = sale_request.customer_name = customer_name
#
#     # logger.warning(f'HireRequest: {str(hire_request)}')
#
#     with pycommence_context(CsrName.Hire) as pycmc:
#         # todo filter_array
#         hires, more_hires = await gather_records_gen(pycmc, hire_request)
#
#     with pycommence_context(CsrName.Sale) as pycmc:
#         sales, more_sales = await gather_records_gen(pycmc, sale_request)
#
#     records: list[AMHERST_ORDER_MODELS] = hires + sales
#     records.sort(key=lambda x: x.send_date, reverse=True)
#     response = SearchResponseMulti(records=records, search_request=[hire_request, sale_request])
#     logger.debug(str(response))
#     return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})
