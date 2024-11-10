from __future__ import annotations

import contextlib

from comtypes import CoInitialize, CoUninitialize
from fastapi import Depends, Query
from loguru import logger
from pydantic import BaseModel
from starlette.exceptions import HTTPException

from amherst.back.backend_search_paginate import Pagination, SearchRequest, SearchResponse
from shipaw.models.pf_msg import ShipmentResponse
from shipaw.models.pf_shipment import Shipment
from pycommence.filters import ConditionType, ConnectedFieldFilter, FieldFilter, FilterArray
from pycommence.pycmc_types import MoreAvailable
from pycommence.pycommence_v2 import PyCommence
from amherst.models.amherst_models import AMHERST_TABLE_MODELS
from amherst.models.commence_adaptors import CustomerAliases, HireAliases
from amherst.models.maps import AmherstTableName, CMAP, record_model


@contextlib.contextmanager
def pycommence_context(csrname: AmherstTableName, filter_array: FilterArray | None = None) -> PyCommence:
    CoInitialize()
    pyc = PyCommence.with_csr(csrname, filter_array=filter_array)
    yield pyc
    CoUninitialize()


async def fil_array_from_search_request(q: SearchRequest) -> FilterArray | None:
    if not any([q.row_id, q.pk_value]):
        cmap = CMAP[q.csrname]
        fil_array = cmap.default_filter if q.filtered else FilterArray()

        if q.customer_name:
            customer_filter = FieldFilter(
                column=CustomerAliases.CUSTOMER_NAME,
                condition=q.condition,
                value=q.customer_name,
            )
            if cmap.category == AmherstTableName.Customer:
                fil = customer_filter
            elif cust_con := cmap.customer_connection:
                fil = ConnectedFieldFilter.from_fil(field_fil=customer_filter, connection=cust_con)
            else:
                raise ValueError(f'No customer connection for {cmap.category}')
            fil_array.add_filter(fil)
            # if fils := search_dict.get('filters'):
            #     fil_array.add_filters(*fils)
        return fil_array
    return None


async def fil_array_dep(
    q: SearchRequest = Depends(SearchRequest.from_query),
) -> FilterArray | None:
    return await fil_array_from_search_request(q)


async def pycmc_f_query(
    csrname: AmherstTableName = Query(...),
    fil_array: FilterArray | None = Depends(fil_array_dep),
) -> PyCommence:
    with pycommence_context(csrname=csrname, filter_array=fil_array) as pycmc:
        yield pycmc


async def gather_records(
    input_type: type[AMHERST_TABLE_MODELS],
    pycmc: PyCommence,
    sq: SearchRequest,
    get_id: bool = True,
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


async def gather_records2(
    pycmc: PyCommence,
    csrname: AmherstTableName,
    pagination: Pagination = Pagination(),
    get_id: bool = True,
) -> tuple[list[AMHERST_TABLE_MODELS], MoreAvailable | None]:
    input_type: type[AMHERST_TABLE_MODELS] = CMAP[csrname].record_model

    records = []
    more = None

    for row in pycmc.read_rows(
        csrname=csrname,
        with_category=True,
        pagination=pagination,
        with_id=get_id,
    ):
        if isinstance(row, MoreAvailable):
            more = row
            break
        records.append(input_type.model_validate(row))
    return records, more


async def pycommence_search(
    search_request: SearchRequest,
    pycmc: PyCommence,
):
    record_type: type[BaseModel] = await record_model(search_request.csrname)

    record = None
    if search_request.row_id:
        record = pycmc.read_row(csrname=search_request.csrname, id=search_request.row_id)
    elif search_request.pk_value:
        record = pycmc.read_row(csrname=search_request.csrname, pk=search_request.pk_value)
    if record:
        validated = record_type.model_validate(record)
        return SearchResponse(records=[validated], more=None, search_request=search_request)

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
        logger.debug(f'Logged tracking for {category} {record.pk_value}')

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
