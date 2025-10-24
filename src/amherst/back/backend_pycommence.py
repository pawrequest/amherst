"""
Module for backend integration with PyCommence data sources.

Provides async functions for querying, fetching, and searching records
using PyCommence, with support for pagination and filtering.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from fastapi import Depends, Query
from loguru import logger
from pycommence.cursor import RESULTS_GENERATOR
from pycommence.exceptions import PyCommenceNotFoundError
from pycommence.pycmc_types import RowData
from starlette.exceptions import HTTPException
from pycommence import MoreAvailable, PyCommence, pycommence_context, pycommences_context

from amherst.back.backend_search_paginate import SearchRequest, SearchResponse, MoreAvailableFront
from amherst.models.commence_adaptors import CursorName, AmherstRowInfo
from amherst.models.maps import CategoryName, mapper_from_query_csrname
from amherst.models.meta import TABLE_REGISTER, get_table_model
from amherst.models.amherst_models import AmherstShipableBase


async def pycmc_f_query(
    csrname: CursorName = Query(...),
) -> AsyncGenerator[PyCommence, None]:
    with pycommence_context(csrname=csrname) as pycmc:
        yield pycmc


async def pycmcs_f_query(
    csrnames: list[CategoryName] = Query(...),
) -> AsyncGenerator[PyCommence, None]:
    with pycommences_context(csrnames=csrnames) as pycmc:
        yield pycmc


async def pycommence_gather(
    pycmc: PyCommence,
    q: SearchRequest,
) -> tuple[list[AmherstShipableBase], MoreAvailable | None]:
    """
    Gather records from PyCommence based on the provided search request.
    Add MoreAvailable if q has pagination and there are more records to fetch.
    """

    model_type = get_table_model(q.csrname)
    logger.warning('GATHERING')
    more = None
    records = []
    for row in await generate_pycommence_rowdata(pycmc, q):
        if isinstance(row, MoreAvailable):
            more = MoreAvailableFront(n_more=row.n_more, json_link=q.next_q_str_json, html_link=q.next_q_str)
            break
        records.append(convert_pycommence_rowdata(model_type, row))
    return records, more


def convert_pycommence_rowdata[T: type[AmherstShipableBase]](input_type: T, result: RowData) -> T:
    mod = input_type(row_info=result.row_info, **result.data)
    return mod.model_validate(mod)


async def generate_pycommence_rowdata(
    pycmc: PyCommence,
    q: SearchRequest,
) -> RESULTS_GENERATOR:
    logger.debug(f'Generating rows for {q.csrname}')
    mapper = await mapper_from_query_csrname(csrname=q.csrname)
    fil_array = await q.filter_array()
    row_filter_fn = mapper.py_filters[q.py_filter_i] if q.py_filter_i else None
    return pycmc.read_rows(
        csrname=q.csrname,
        pagination=q.pagination,
        row_filter=row_filter_fn,
        filter_array=fil_array,
    )


async def pycommence_fetch(
    q: SearchRequest,
    pycmc: PyCommence,
) -> AmherstShipableBase | None:
    row_id = None
    if q.row_id:
        row_id = q.row_id
    elif q.pk_value:
        try:
            row_id = pycmc.csr(q.csrname).pk_to_id(q.pk_value)
        except PyCommenceNotFoundError:
            ...
    if row_id:
        row = pycmc.read_row(csrname=q.csrname, row_id=row_id)
        # mapper = await mapper_from_query_csrname(csrname=q.csrname)
        # res = mapper.record_model(row_info=row.row_info, **row.data)
        model_type = TABLE_REGISTER.get(q.csrname)
        res = model_type(row_info=row.row_info, **row.data)
        return res
    return None


async def pycommence_fetch_f_info(
    row_info: AmherstRowInfo,
) -> AmherstShipableBase | None:
    with pycommence_context(csrname=row_info.category) as pycmc:
        row = pycmc.read_row(csrname=row_info.category, row_id=row_info.id).data
    model_type = get_table_model(row_info.category)
    return model_type.model_validate(row)


async def pycommence_search(
    q: SearchRequest = Depends(SearchRequest.from_query),
    pycmc: PyCommence = Depends(pycmc_f_query),
) -> SearchResponse:
    if record := await pycommence_fetch(q, pycmc):
        records, more = [record], None
    else:
        records, more = await pycommence_gather(pycmc=pycmc, q=q)

    resp = SearchResponse(records=records, more=more, search_request=q)

    if q.max_rtn and resp.length > q.max_rtn:
        raise HTTPException(
            status_code=404,
            detail=f'Too many items found: Specified {q.max_rtn} rows and returned {resp.length}',
        )
    return resp


async def pycommence_get_one(
    search_request: SearchRequest = Depends(SearchRequest.from_query),
    pycmc: PyCommence = Depends(pycmc_f_query),
) -> AmherstShipableBase:
    search_request.max_rtn = 1
    res = await pycommence_fetch(search_request, pycmc)
    if not res:
        logger.warning('No Results')
    return res

