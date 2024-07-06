from __future__ import annotations

from typing import Self

from comtypes import CoInitialize, CoUninitialize
from fastapi import Body, Depends, Path, Query
from loguru import logger
from pydantic import BaseModel, model_validator
from sqlmodel import SQLModel

from amherst.models.amherst_models import (
    AMHERST_TABLE_TYPES,
    AmherstCustomerDB,
    AmherstHireDB,
    AmherstSaleDB,
    TYPES_MAP,
)
from pycommence.pycommence_v2 import PyCommence
from shipaw.expresslink_client import ELClient

PAGE_SIZE = 20


class MoreAvailable:
    ...


class SearchResponse[T:AMHERST_TABLE_TYPES](BaseModel):
    records: list[T]
    more: bool
    pagination: Pagination
    length: int = None

    @model_validator(mode='after')
    def set_length(self):
        if self.length is None and self.records:
            self.length = len(self.records)
        return self


class Pagination(BaseModel):
    offset: int = 0
    limit: int | None = PAGE_SIZE

    @classmethod
    def from_query(cls, limit: int | None = Query(PAGE_SIZE), offset: int = Query(0)) -> Self:
        logger.debug(f'Pagination.from_query({limit=}, {offset=})')
        return cls(limit=limit, offset=offset)


async def model_type_from_path(csrname: str = Path(...)) -> type[SQLModel]:
    match csrname.lower():
        case 'hire':
            return AmherstHireDB
        case 'sale':
            return AmherstSaleDB
        case 'customer':
            return AmherstCustomerDB


async def template_name_from_path(csrname: str = Path(...)):
    return TYPES_MAP[csrname]['template']


async def template_name_from_body(csrname: str = Body('')):
    return TYPES_MAP[csrname]['template']


async def get_pyc_query(csrname: str = Query(...)) -> PyCommence:
    CoInitialize()
    pyc = PyCommence.with_csr(csrname)
    yield pyc
    CoUninitialize()


async def get_pyc_body(csrname: str = Body(...)) -> PyCommence:
    CoInitialize()
    pyc = PyCommence.with_csr(csrname)
    yield pyc
    CoUninitialize()


async def search_query[T: SearchResponse](
        pycmc: PyCommence = Depends(get_pyc_query),
        csrname: str = Query(...),
        pk_value: str = Query(''),
        pagination: Pagination = Depends(Pagination.from_query),
) -> T:
    return await make_response(csrname, pagination, pk_value, pycmc)


async def search_body[T: SearchResponse](
        pycmc: PyCommence = Depends(get_pyc_body),
        csrname: str = Body(''),
        pk_value: str = Body(''),
        pagination: Pagination = Depends(Pagination.from_query),
) -> T:
    return await make_response(csrname, pagination, pk_value, pycmc)


async def make_response(csrname, pagination, pk_value, pycmc):
    input_type: type[SQLModel] = TYPES_MAP[csrname]['input_type']
    more = False
    records = []
    async for row in do_search_more(csrname, pk_value, pycmc, pagination):
        if isinstance(row, MoreAvailable):
            more = True
            break
        records.append(input_type.model_validate(row))
    return SearchResponse(records=records, more=more, pagination=pagination)


async def do_search_more(
        csrname: str,
        pk_value: str,
        pycmc: PyCommence,
        pagination: Pagination,
):
    for rownum, row in enumerate(
            pycmc.read_rows_pk_contains(
                pk_value,
                csrname=csrname,
                count=pagination.limit + 1,
                offset=pagination.offset,
                with_category=True
            ), start=1
    ):
        yield MoreAvailable() if rownum > pagination.limit else row


def get_el_client() -> ELClient:
    try:
        return ELClient()
    except Exception as e:
        logger.error(f'get_pfc: {e}')
        raise
