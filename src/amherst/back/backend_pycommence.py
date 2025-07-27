from __future__ import annotations

from typing import AsyncGenerator

from fastapi import Depends, Query
from loguru import logger
from pycommence.exceptions import PyCommenceNotFoundError
from pycommence.pycmc_types import RowInfo
from starlette.exceptions import HTTPException
from pycommence import MoreAvailable, PyCommence, pycommence_context, pycommences_context

from amherst.back.backend_search_paginate import SearchRequest, SearchResponse
from amherst.models.amherst_models import AMHERST_TABLE_MODELS
from amherst.models.commence_adaptors import CursorName
from amherst.models.maps import CategoryName, mapper_from_query_csrname


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
) -> tuple[list[AMHERST_TABLE_MODELS], MoreAvailable | None]:
    mapper = await mapper_from_query_csrname(csrname=q.csrname)
    input_type = mapper.record_model
    fil_array = await q.filter_array()
    py_filter = getattr(mapper.py_filters, q.py_filter) if q.py_filter else None
    rowgen = pycmc.read_rows(
        csrname=q.csrname,
        pagination=q.pagination,
        row_filter=py_filter,
        filter_array=fil_array,
    )
    records = []
    more = None
    for row in rowgen:
        if isinstance(row, MoreAvailable):
            more = row
            more.json_link = q.next_q_str_json
            more.html_link = q.next_q_str
            break
        records.append(input_type.model_validate(row))
    return records, more


async def pycommence_fetch(
    q: SearchRequest,
    pycmc: PyCommence,
) -> AMHERST_TABLE_MODELS | None:
    row_id = None
    if q.row_id:
        row_id = q.row_id
    elif q.pk_value:
        try:
            row_id = pycmc.csr(q.csrname).pk_to_id(q.pk_value)
        except PyCommenceNotFoundError as e:
            ...
    if row_id:
        row = pycmc.read_row2(csrname=q.csrname, row_id=row_id).data
        row['row_id'] = row_id
        mapper = await mapper_from_query_csrname(csrname=q.csrname)
        return mapper.record_model.model_validate(row)


async def pycommence_fetch_f_info(
    row_info: RowInfo,
) -> AMHERST_TABLE_MODELS | None:
    with pycommence_context(csrname=row_info.category) as pycmc:
        row = pycmc.read_row2(csrname=row_info.category, row_id=row_info.id).data
    mapper = await mapper_from_query_csrname(csrname=CategoryName(row_info.category))
    return mapper.record_model.model_validate(row)


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
) -> AMHERST_TABLE_MODELS:
    search_request.max_rtn = 1
    res = await pycommence_fetch(search_request, pycmc)
    if not res:
        logger.warning('No Results')
    return res


