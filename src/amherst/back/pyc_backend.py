from __future__ import annotations

import contextlib
from copy import deepcopy

from comtypes import CoInitialize, CoUninitialize
from loguru import logger
from pydantic import BaseModel

from amherst.back.route_depends import CsrName, SearchRequest, SearchResponse
from amherst.models.maps import CURSOR_MAP
from pycommence.filters import FilterArray
from pycommence.pycmc_types import MoreAvailable
from pycommence.pycommence_v2 import PyCommence


@contextlib.contextmanager
def get_pyc(csrname: CsrName, filter_array: FilterArray | None = None) -> PyCommence:
    # CoInitialize()
    # logger.warning('CoInitialize')
    pyc = PyCommence.with_csr(csrname, filter_array=filter_array)
    yield pyc
    # CoUninitialize()
    # logger.warning('CoUninitialize')


async def pk_search(
        pycmc: PyCommence,
        sq: SearchRequest,
):
    filter_array = pycmc.csr(sq.csrname).pk_filter_array(pk=sq.pk_value, condition=sq.condition)
    for row in pycmc.read_rows(
            csrname=sq.csrname,
            with_category=True,
            pagination=sq.pagination,
            filter_array=filter_array
    ):
        yield row


async def gather_records(input_type, pycmc: PyCommence, sq):
    records = []
    more = None
    async for row in pk_search(pycmc, sq):
        if isinstance(row, MoreAvailable):
            more = row
            more.json_link = sq.next_q_str_json
            more.html_link = sq.next_q_str
            break
        records.append(input_type.model_validate(row))
    return more, records


async def pycommence_response[T: SearchResponse](
        search_request: SearchRequest,
) -> T:
    logger.warning('CoInitialize')
    CoInitialize()
    pycmc = PyCommence.with_csr(search_request.csrname)
    csr = pycmc.csr(search_request.csrname)
    array = deepcopy(search_request.filter_array(csr))

    pycmc.set_csr(search_request.csrname, filter_array=array)

    record_type: type[BaseModel] = CURSOR_MAP[search_request.csrname]['input_type']
    more, records = await gather_records(input_type=record_type, pycmc=pycmc, sq=search_request)
    try:
        return SearchResponse(records=records, more=more, search_request=search_request)
    finally:
        CoUninitialize()
        logger.warning('CoUninitialize')
