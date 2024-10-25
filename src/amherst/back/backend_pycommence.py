from __future__ import annotations

import contextlib

from comtypes import CoInitialize, CoUninitialize
from fastapi import Depends, Path
from loguru import logger
from pydantic import BaseModel
from pycommence.filters import FilterArray
from pycommence.pycmc_types import MoreAvailable
from pycommence.pycommence_v2 import PyCommence

from amherst.back.search_paginate import SearchRequest, SearchResponse
from amherst.models.amherst_models import AMHERST_TABLE_MODELS
from amherst.models.maps import AmherstTableName, CURSOR_MAP


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


# async def pk_search(
#     pycmc: PyCommence,
#     sq: SearchRequest,
#     get_id: bool = False,
# ):
#     filter_array = pycmc.csr(sq.csrname).pk_filter_array(pk=sq.pk_value, condition=sq.condition)
#     for row in pycmc.read_rows(
#         csrname=sq.csrname,
#         with_category=True,
#         pagination=sq.pagination,
#         filter_array=filter_array,
#         get_id=get_id,
#     ):
#         yield row


#
async def gather_records(input_type, pycmc: PyCommence, sq: SearchRequest, get_id: bool = True):
    records = []
    more = None
    for row in pycmc.read_rows(
            csrname=sq.csrname,
            with_category=True,
            pagination=sq.pagination,
            get_id=get_id,
    ):
        if isinstance(row, MoreAvailable):
            more = row
            more.json_link = sq.next_q_str_json
            more.html_link = sq.next_q_str
            break
        records.append(input_type.model_validate(row))
    return more, records


# async def search_f_query(
#     search_request: SearchRequest = Depends(SearchRequest.from_query),
#     pycmc: PyCommence = Depends(pycmc_f_path),
# ) -> SearchResponse:
#     return await pycommence_search(pycmc, search_request)


async def search_f_path(
        search_request: SearchRequest = Depends(SearchRequest.from_path),
        pycmc: PyCommence = Depends(pycmc_f_path),
) -> SearchResponse:
    return await pycommence_search(pycmc, search_request)


async def pycommence_search1(
        pycmc: PyCommence,
        search_request: SearchRequest,
):
    csr = pycmc.csr(search_request.csrname)
    if array := search_request.src_filter(csr):
        pycmc.set_csr(search_request.csrname, filter_array=array)
    record_type: type[BaseModel] = CURSOR_MAP[search_request.csrname]['input_type']
    more, records = await gather_records(input_type=record_type, pycmc=pycmc, sq=search_request)
    return SearchResponse(records=records, more=more, search_request=search_request)


async def pycommence_search(
        pycmc: PyCommence,
        search_request: SearchRequest,
):
    csr = pycmc.csr(search_request.csrname)
    record_type: type[BaseModel] = CURSOR_MAP[search_request.csrname]['input_type']

    if search_request.row_id:
        record = pycmc.read_row(id=search_request.row_id)
        validated = record_type.model_validate(record)
        return SearchResponse(records=[validated], more=None, search_request=search_request)

    if search_request.pk_value:
        fil = csr.pk_filter_array(pk=search_request.pk_value, condition=search_request.condition)
        pycmc.set_csr(search_request.csrname, filter_array=fil)

    more, records = await gather_records(input_type=record_type, pycmc=pycmc, sq=search_request)
    return SearchResponse(records=records, more=more, search_request=search_request)


async def pycommence_response(
        search_request: SearchRequest,
) -> SearchResponse:
    with pycommence_context(search_request.csrname) as pycmc:
        return await pycommence_search(pycmc, search_request)


def row_from_path_id(
        csrname: AmherstTableName = Path(...),
        row_id: str = Path(...),
) -> AMHERST_TABLE_MODELS:
    record_type: type[BaseModel] = CURSOR_MAP[csrname]['input_type']

    with pycommence_context(csrname=csrname) as pycmc:
        row = pycmc.read_row(id=row_id)
    return record_type.model_validate(row)
