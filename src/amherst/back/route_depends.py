from __future__ import annotations

from comtypes import CoInitialize, CoUninitialize
from fastapi import Body, Depends, Query

from amherst.back.route_depends_types import CsrName, Pagination, SearchQuery, SearchResponse
from amherst.models.maps import CURSOR_MAP
from pycommence.pycommence_v2 import PyCommence


async def template_name_from_query(csrname: CsrName = Query(...)):
    return CURSOR_MAP[csrname]['template']


async def get_pyc_query(csrname: CsrName = Query(...)) -> PyCommence:
    CoInitialize()
    pyc = PyCommence.with_csr(csrname)
    yield pyc
    CoUninitialize()


async def get_pyc_body(csrname: CsrName = Body(...)) -> PyCommence:
    CoInitialize()
    pyc = PyCommence.with_csr(csrname)
    yield pyc
    CoUninitialize()


async def search_get[T: SearchResponse](
        pycmc: PyCommence = Depends(get_pyc_query),
        csrname: CsrName = Query(...),
        pk_value: str = Query(''),
        pagination: Pagination = Depends(Pagination.from_query),
) -> T:
    sq = SearchQuery(csrname=csrname, pagination=pagination, pk_value=pk_value)
    res = await SearchResponse.from_query(sq=sq, pycmc=pycmc)
    return res


async def search_post[T: SearchResponse](
        search_q: SearchQuery = Depends(SearchQuery.from_body),
) -> T:
    CoInitialize()
    try:
        pycmc = PyCommence.with_csr(search_q.csrname, filter_array=search_q.filter_array)
        return await SearchResponse.from_query(sq=search_q, pycmc=pycmc)

    finally:
        CoUninitialize()
