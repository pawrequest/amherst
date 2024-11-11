from __future__ import annotations

import contextlib

from comtypes import CoInitialize, CoInitializeEx, CoUninitialize
from fastapi import Depends, Query
from loguru import logger
from starlette.exceptions import HTTPException

from amherst.back.backend_search_paginate import SearchRequest, SearchResponse
from pycommence.filters import ConditionType, FilterArray
from pycommence.pycmc_types import MoreAvailable
from pycommence.pycommence_v2 import PyCommence
from amherst.models.amherst_models import AMHERST_TABLE_MODELS
from amherst.models.maps import AmherstMapping, AmherstTableName, mapper_csrname, maps2


@contextlib.contextmanager
def pycommence_context(csrname: AmherstTableName, filter_array: FilterArray | None = None) -> PyCommence:
    CoInitialize()
    pyc = PyCommence.with_csr(csrname, filter_array=filter_array)
    yield pyc
    CoUninitialize()


@contextlib.contextmanager
def pycommence_context2(csrname: AmherstTableName, filter_array: FilterArray | None = None) -> PyCommence:
    try:
        # CoInitialize silently fails if already initialized, so track explicitly
        CoInitialize()

        pyc = PyCommence.with_csr(csrname, filter_array=filter_array)
        yield pyc

    finally:
        CoUninitialize()  # Uninitialize, ignoring if it's already done
    # if not CoInitializeEx(0):
    #     initialized = True
    # else:
    #     initialized = False
    #
    # pyc = PyCommence.with_csr(csrname, filter_array=filter_array)
    # yield pyc
    #
    # if initialized:
    #     CoUninitialize()


async def pycmc_f_query(
    csrname: AmherstTableName = Query(...),
    q: SearchRequest = Depends(SearchRequest.from_query),
) -> PyCommence:
    with pycommence_context(csrname=csrname, filter_array=q.filter_array()) as pycmc:
        yield pycmc


async def gather_records_gen(
    pycmc: PyCommence, q: SearchRequest, mapper: AmherstMapping = Depends(maps2)
) -> tuple[list[AMHERST_TABLE_MODELS], MoreAvailable | None]:
    input_type = mapper.record_model
    fil_array = q.filter_array()
    pycmc.csr(q.csrname).filter_array = fil_array
    row_filter = mapper.filter_map_row.loose if q.py_filter else None
    # row_filter = mapper.row_filter if q.py_filter else None

    rows_left = pycmc.csr(q.csrname).row_count - q.pagination.end if q.pagination.end else 0

    rowgen = pycmc.read_rows(
        csrname=q.csrname,
        pagination=q.pagination,
        row_filter=row_filter,
    )

    records = [input_type.model_validate(row) for row in rowgen]
    more = MoreAvailable(n_more=rows_left, json_link=q.next_q_str_json, html_link=q.next_q_str) if rows_left else None
    return records, more


async def pycommence_search(
    q: SearchRequest,
    pycmc: PyCommence,
) -> AMHERST_TABLE_MODELS | None:
    record = None
    if q.row_id:
        record = pycmc.read_row(csrname=q.csrname, id=q.row_id)
    elif q.pk_value:
        if q.condition == ConditionType.EQUAL:
            record = pycmc.read_row(csrname=q.csrname, pk=q.pk_value)
    if record:
        mapper = await mapper_csrname(csrname=q.csrname)
        return mapper.record_model.model_validate(record)


async def pycommence_response(
    q: SearchRequest = Depends(SearchRequest.from_query),
    pycmc: PyCommence = Depends(pycmc_f_query),
    mapper: AmherstMapping = Depends(maps2),
) -> AMHERST_TABLE_MODELS | SearchResponse:
    if record := await pycommence_search(q, pycmc):
        records, more = [record], None
    else:
        records, more = await gather_records_gen(pycmc=pycmc, q=q, mapper=mapper)

    resp = SearchResponse(records=records, more=more, search_request=q)

    if q.max_rtn and resp.length > q.max_rtn:
        raise HTTPException(
            status_code=404,
            detail=f'Too many items found: Specified {q.max_rtn} rows and returned {resp.length}',
        )
    return resp


async def get_one(
    search_request: SearchRequest = Depends(SearchRequest.from_query),
    pycmc: PyCommence = Depends(pycmc_f_query),
) -> AMHERST_TABLE_MODELS:
    search_request.max_rtn = 1
    return await pycommence_search(search_request, pycmc)


def record_tracking(record, shipment_response):
    record = record
    try:
        category = record.category
        if category == 'Customer':
            logger.error('CANT LOG TO CUSTOMER')
            return
        # do_record_tracking(record, shipment_response)
        logger.debug(f'Logged tracking for {category} {record.pk_value}')

    except Exception as exce:
        logger.exception(exce)
        raise


# def do_record_tracking(shipment: Shipment, shipment_response: ShipmentResponse, pycmc: PyCommence):
#     tracking_link = shipment_response.tracking_link()
#     cmc_package = (
#         {
#             HireAliases.TRACK_IN: tracking_link,
#             HireAliases.ARRANGED_IN: True,
#             HireAliases.PICKUP_DATE: f'{shipment.shipping_date:%Y-%m-%d}',
#         }
#         if shipment.direction in ['in', 'dropoff']
#         else {HireAliases.TRACK_OUT: tracking_link, HireAliases.ARRANGED_OUT: True}
#     )
#
#     pycmc.update_row(cmc_package)
#     logger.debug(f'Logged {str(cmc_package)} to Commence')


# async def pycommence_search2(
#     search_request: SearchRequest,
#     pycmc: PyCommence,
#     with_id: bool = True,
# ) -> SearchResponse:
#     logger.debug(f'pycommence_search({search_request=}, {pycmc=})')
#     record_type: type[BaseModel] = await record_model(search_request.csrname)
#     # record_type: type[BaseModel] = CURSOR_MAP[search_request.csrname]['input_type']
#     csr = pycmc.csr(search_request.csrname)
#
#     if search_request.row_id:
#         record = pycmc.read_row(id=search_request.row_id)
#         validated = record_type.model_validate(record)
#         return SearchResponse(records=[validated], more=None, search_request=search_request)
#
#     if search_request.pk_value:
#         fil = csr.pk_filter_array(pk=search_request.pk_value, condition=search_request.condition)
#         pycmc.set_csr(search_request.csrname, filter_array=fil)
#
#     async def gather_records():
#         _records = []
#         _more = None
#         for row in pycmc.read_rows(
#             csrname=search_request.csrname,
#             with_category=True,
#             pagination=search_request.pagination,
#             with_id=with_id,
#         ):
#             if isinstance(row, MoreAvailable):
#                 _more = row
#                 _more.json_link = search_request.next_q_str_json
#                 _more.html_link = search_request.next_q_str
#                 break
#             _records.append(record_type.model_validate(row))
#         return _more, _records
#
#     more, records = await gather_records()
#     return SearchResponse(records=records, more=more, search_request=search_request)


# async def pycmc_f_body(
#     csrname: AmherstTableName = Body(...),
#     row_id: str = Body(None),
#     pk_value: str = Body(None),
#     search_dict: dict | None = Body(None),
#     dflt_filter: bool = Body(False),
# ):
#     if any([row_id, pk_value]):
#         fil_array = None
#     else:
#         cmap = CMAP[csrname]
#         fil_array = await fil_array_from(cmap, dflt_filter, search_dict.get('customer_name'))
#
#     logger.warning('this likely buggy due to cmc filter logic')
#     with pycommence_context(csrname=csrname, filter_array=fil_array) as pycmc:
#         yield pycmc

# pycmc.set_csr(csrname, filter_array=fil_array)
# yield pycommence_context(csrname=csrname, filter_array=fil_array)
