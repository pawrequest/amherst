from __future__ import annotations

import contextlib

from comtypes import CoInitialize, CoUninitialize
from fastapi import Depends, Path
from loguru import logger
from pydantic import BaseModel
from win32pdhquery import Query
from starlette.exceptions import HTTPException

from shipaw.models.pf_msg import ShipmentResponse
from shipaw.models.pf_shipment import Shipment
from pycommence.filters import FilterArray
from pycommence.pycmc_types import MoreAvailable
from pycommence.pycommence_v2 import PyCommence
from amherst.back.backend_search_paginate import SearchRequest, SearchResponse
from amherst.models.amherst_models import AMHERST_TABLE_MODELS
from amherst.models.commence_adaptors import HireAliases
from amherst.models.maps import AmherstTableName, CMAP, record_model


@contextlib.contextmanager
def pycommence_context(csrname: AmherstTableName, filter_array: FilterArray | None = None) -> PyCommence:
    CoInitialize()
    logger.debug('CoInitialize')
    pyc = PyCommence.with_csr(csrname, filter_array=filter_array)
    yield pyc
    CoUninitialize()
    logger.debug('CoUninitialize')


async def pycmc_f_path(csrname: AmherstTableName = Path(...)) -> PyCommence:
    with pycommence_context(csrname=csrname) as pycmc:
        yield pycmc


async def pycmc_f_query(csrname: AmherstTableName = Query(...)) -> PyCommence:
    with pycommence_context(csrname=csrname) as pycmc:
        yield pycmc


async def gather_records(
    input_type: type[AMHERST_TABLE_MODELS],
    # pycmc: PyCommence,
    sq: SearchRequest,
    get_id: bool = True,
    pycmc: PyCommence = Depends(pycmc_f_path),
):
    records = []
    more = None
    for row in pycmc.read_rows(
        csrname=sq.csrname,
        with_category=True,
        pagination=sq.pagination,
        with_id=get_id,
    ):
        if isinstance(row, MoreAvailable):
            more = row
            more.json_link = sq.next_q_str_json
            more.html_link = sq.next_q_str
            break
        records.append(input_type.model_validate(row))
    return more, records


async def pycommence_search(
    search_request: SearchRequest,
    pycmc: PyCommence,
):
    csr = pycmc.csr(search_request.csrname)
    record_type: type[BaseModel] = await record_model(search_request.csrname)

    if search_request.row_id:
        record = pycmc.read_row(id=search_request.row_id)
        validated = record_type.model_validate(record)
        return SearchResponse(records=[validated], more=None, search_request=search_request)

    fil = FilterArray()
    logger.warning('this likely buggy due to logic in FilterArray')
    if search_request.filtered:
        fil = CMAP[search_request.csrname].default_filter

    if search_request.pk_value:
        fil.add_filter(csr.pk_filter(pk=search_request.pk_value, condition=search_request.condition))

    pycmc.set_csr(search_request.csrname, filter_array=fil)
    more, records = await gather_records(input_type=record_type, pycmc=pycmc, sq=search_request)

    return SearchResponse(records=records, more=more, search_request=search_request)


async def pycommence_response(
    search_request: SearchRequest = Depends(SearchRequest.from_query),
    pycmc: PyCommence = Depends(pycmc_f_query),
) -> SearchResponse:
    resp = await pycommence_search(search_request, pycmc)
    if search_request.max_rtn and resp.length > search_request.max_rtn:
        raise HTTPException(
            status_code=404,
            detail=f'Too many items found: Specified {search_request.max_rtn} rows and returned {resp.length}',
        )
    return resp


async def get_one(
    search_request: SearchRequest = Depends(SearchRequest.from_query),
    pycmc: PyCommence = Depends(pycmc_f_query),
) -> AMHERST_TABLE_MODELS:
    search_request.max_rtn = 1
    resp = await pycommence_search(search_request, pycmc)
    if resp.length == 1:
        return resp.records[0]
    elif resp.length == 0:
        raise ValueError(f'No {search_request.csrname} record found for {search_request.pk_value}')


def record_tracking(record, shipment_response):
    record = record
    try:
        category = record.category
        if category == 'Customer':
            logger.error('CANT LOG TO CUSTOMER')
            return
        do_record_tracking(record, shipment_response)
        logger.debug(f'Logged tracking for {category} {record.name}')

    except Exception as exce:
        logger.exception(exce)
        raise


def do_record_tracking(shipment: Shipment, shipment_response: ShipmentResponse, pycmc: PyCommence):
    tracking_link = shipment_response.tracking_link()
    cmc_package = (
        {
            HireAliases.TRACK_IN: tracking_link,
            HireAliases.ARRANGED_IN: True,
            HireAliases.PICKUP_DATE: f'{shipment.shipping_date:%Y-%m-%d}',
        }
        if shipment.direction in ['in', 'dropoff']
        else {HireAliases.TRACK_OUT: tracking_link, HireAliases.ARRANGED_OUT: True}
    )

    pycmc.update_row(cmc_package)
    logger.debug(f'Logged {str(cmc_package)} to Commence')


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
