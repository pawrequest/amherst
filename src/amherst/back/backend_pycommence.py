from __future__ import annotations

import contextlib

from comtypes import CoInitialize, CoUninitialize
from fastapi import Depends, Path
from loguru import logger
from pydantic import BaseModel
from starlette.requests import Request

from pycommence.filters import FilterArray
from pycommence.pycmc_types import MoreAvailable
from pycommence.pycommence_v2 import PyCommence
from amherst.back.search_paginate import SearchRequest, SearchResponse
from amherst.models.amherst_models import AMHERST_TABLE_MODELS
from amherst.models.maps import AmherstTableName, record_model, CMAP


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


# async def search_f_query(
#     search_request: SearchRequest = Depends(SearchRequest.from_query),
#     pycmc: PyCommence = Depends(pycmc_f_path),
# ) -> SearchResponse:
#     return await pycommence_search(pycmc, search_request)


async def search_f_path(
        search_request: SearchRequest = Depends(SearchRequest.from_path),
        # pycmc: PyCommence = Depends(pycmc_f_path),
) -> SearchResponse:
    return await pycommence_search(search_request)
    # return await pycommence_search(search_request, pycmc)


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
        # def_fils = CMAP[search_request.csrname].default_filter.filters
        # fil.add_filters(def_fils)

    if search_request.pk_value:
        pk_filter = csr.pk_filter(pk=search_request.pk_value, condition=search_request.condition)
        fil.add_filter(pk_filter)
        # fil = csr.pk_filter_array(pk=search_request.pk_value, condition=search_request.condition)

    pycmc.set_csr(search_request.csrname, filter_array=fil)
    more, records = await gather_records(input_type=record_type, pycmc=pycmc, sq=search_request)
    return SearchResponse(records=records, more=more, search_request=search_request)


async def pycommence_response(
        # request: Request,
        search_request: SearchRequest,

) -> SearchResponse:
    with pycommence_context(search_request.csrname) as pycmc:
        return await pycommence_search(search_request, pycmc)
    # return await pycommence_search(search_request)


async def pycommence_response2(
        # request: Request,
        search_request: SearchRequest,


) -> SearchResponse:
    with pycommence_context(search_request.csrname) as pycmc:
        return await pycommence_search(search_request, pycmc)
    # return await pycommence_search(search_request)


def row_from_path_id(
        csrname: AmherstTableName = Path(...),
        row_id: str = Path(...),
        # pycmc: PyCommence = Depends(pycmc_f_path),
        record_type: type[BaseModel] = Depends(record_model),
) -> AMHERST_TABLE_MODELS:
    # record_type: type[BaseModel] = CURSOR_MAP[csrname]['input_type']
    with pycommence_context(csrname=csrname) as pycmc:
        row = pycmc.read_row(id=row_id)
    # row = pycmc.read_row(id=row_id)
    return record_type.model_validate(row)



async def pycommence_search2(
        search_request: SearchRequest,
        pycmc: PyCommence,
        with_id: bool = True,
) -> SearchResponse:
    logger.debug(f'pycommence_search({search_request=}, {pycmc=})')
    record_type: type[BaseModel] = await record_model(search_request.csrname)
    # record_type: type[BaseModel] = CURSOR_MAP[search_request.csrname]['input_type']
    csr = pycmc.csr(search_request.csrname)

    if search_request.row_id:
        record = pycmc.read_row(id=search_request.row_id)
        validated = record_type.model_validate(record)
        return SearchResponse(records=[validated], more=None, search_request=search_request)

    if search_request.pk_value:
        fil = csr.pk_filter_array(pk=search_request.pk_value, condition=search_request.condition)
        pycmc.set_csr(search_request.csrname, filter_array=fil)

    async def gather_records():
        _records = []
        _more = None
        for row in pycmc.read_rows(
                csrname=search_request.csrname,
                with_category=True,
                pagination=search_request.pagination,
                with_id=with_id,
        ):
            if isinstance(row, MoreAvailable):
                _more = row
                _more.json_link = search_request.next_q_str_json
                _more.html_link = search_request.next_q_str
                break
            _records.append(record_type.model_validate(row))
        return _more, _records

    more, records = await gather_records()
    return SearchResponse(records=records, more=more, search_request=search_request)

