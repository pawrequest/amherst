from __future__ import annotations

from typing import NamedTuple, Self

from comtypes import CoInitialize, CoUninitialize
from fastapi import Body, Depends, Path, Query
from loguru import logger
from sqlmodel import SQLModel, Session, select

from amherst.db import get_session
from amherst.models.am_record_smpl import (
    AMHERST_TABLE_TYPES,
    AmherstCustomerDB,
    AmherstHireDB,
    AmherstSaleDB,
    TYPES_MAP,
    dict_to_amtable,
)
from amherst.sql import stmt_from_q
from pycommence.pycommence_v2 import PyCommence
from shipaw.expresslink_client import ELClient

PAGE_SIZE = 20


class Pagination(NamedTuple):
    offset: int = 0
    limit: int | None = PAGE_SIZE

    @classmethod
    def from_query(cls, limit: int | None = Query(PAGE_SIZE), offset: int = Query(0)) -> Self:
        logger.debug(f'Pagination.from_query({limit=}, {offset=})')
        return cls(limit=limit, offset=offset)


async def select_and_more(
        sqlselect,
        session: Session = Depends(get_session),
        pagination: Pagination = Depends(Pagination.from_query)
) -> tuple[list, bool]:
    if pagination.offset:
        sqlselect = sqlselect.offset(pagination.offset)
    if pagination.limit:
        sqlselect = sqlselect.limit(pagination.limit + 1)
    res = session.exec(sqlselect).all()
    if not res:
        return [], False
    more = len(res) > pagination.limit if pagination.limit else False
    return res[: pagination.limit], more


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


async def amrecs_and_more(
        stmt: select = Depends(stmt_from_q),
        session: Session = Depends(get_session),
        pagination: Pagination = Depends(Pagination.from_query),
) -> tuple[list[AMHERST_TABLE_TYPES], bool]:
    return await select_and_more(stmt, session, pagination)


async def get_pyc_body(
        csrname: str = Body(''),
) -> PyCommence:
    yield get_pyc_(csrname)


async def get_pyc_path(
        csrname: str = Path(''),
) -> PyCommence:
    yield get_pyc_(csrname)


async def get_pyc_(csrname):
    CoInitialize()
    pyc = PyCommence.with_csr(csrname)
    yield pyc
    CoUninitialize()


async def search_query[T: AMHERST_TABLE_TYPES](
        pycmc: PyCommence = Depends(get_pyc_path),
        csrname: str = Path(...),
        pk_value: str = Path(...),
        pagination: Pagination = Depends(Pagination.from_query)
) -> list[T]:
    rows = pycmc.read_rows_pk_contains(pk_value, csrname=csrname, count=pagination.limit)
    amrecs = list(map(dict_to_amtable, rows))
    logger.debug(f'{amrecs=}')
    return amrecs


async def search_body[T: AMHERST_TABLE_TYPES](
        pycmc: PyCommence = Depends(get_pyc_body),
        csrname: str = Body(''),
        pk_value: str = Body(''),
        pagination: Pagination = Depends(Pagination.from_query)
) -> list[T]:
    if not all((csrname, pk_value)):
        return []
    rows = list(pycmc.read_rows_pk_contains(pk_value, csrname=csrname, count=pagination.limit))
    amrecs = list(map(dict_to_amtable, rows))
    logger.debug(f'{amrecs=}')
    return amrecs


def get_el_client() -> ELClient:
    try:
        return ELClient()
    except Exception as e:
        logger.error(f'get_pfc: {e}')
        raise
