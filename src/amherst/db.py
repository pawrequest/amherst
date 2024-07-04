from __future__ import annotations

import contextlib
import functools
from typing import NamedTuple, Self

import httpx
import sqlalchemy as sqa
import sqlmodel as sqm
from comtypes import CoInitialize, CoUninitialize
from fastapi import Body, Depends, Path, Query
from loguru import logger
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, and_, or_, select
from starlette.exceptions import HTTPException

from amherst.config import settings
from amherst.models.am_record_smpl import AMHERST_TABLE_TYPES, AmherstCustomerDB, AmherstHireDB, AmherstSaleDB
from pycommence.pycommence_v2 import PyCommence
from shipaw.expresslink_client import ELClient


@functools.lru_cache(maxsize=1)
def get_engine() -> sqa.engine.base.Engine:
    connect_args = {'check_same_thread': False}
    return sqa.create_engine(settings().db_url, echo=False, connect_args=connect_args)
    # return sqa.create_engine('sqlite:///:memory:', echo=False, connect_args=connect_args)


def get_session(engine=None) -> sqm.Session:
    if engine is None:
        engine = get_engine()
    with sqm.Session(engine) as session:
        yield session


@contextlib.contextmanager
def get_session_cm(engine=None):
    if engine is None:
        engine = get_engine()
    with sqm.Session(engine) as session:
        yield session
    session.close()


@contextlib.contextmanager
def get_temporary_session_cm(engine=None):
    if engine is None:
        engine = create_engine('sqlite:///:memory:')
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        try:
            yield session
        finally:
            session.rollback()
            SQLModel.metadata.drop_all(engine)


def get_pycmc_hire() -> PyCommence:
    CoInitialize()
    pyc = PyCommence.with_csr('Hire')
    yield pyc
    CoUninitialize()


async def get_pyc2(
        csrname: str = Path(...),
) -> PyCommence:
    CoInitialize()
    pyc = PyCommence.with_csr(csrname)
    yield pyc
    CoUninitialize()


def get_el_client() -> ELClient:
    try:
        return ELClient()
    except Exception as e:
        logger.error(f'get_pfc: {e}')
        raise


def get_el_client_non_strict() -> ELClient:
    try:
        return ELClient(strict=False)
    except Exception as e:
        logger.error(f'get_pfc: {e}')
        raise


async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client


def create_db(engine=None):
    if engine is None:
        engine = get_engine()
    sqm.SQLModel.metadata.create_all(engine)


PAGE_SIZE = None


class Pagination(NamedTuple):
    offset: int = 0
    limit: int | None = PAGE_SIZE

    @classmethod
    def from_query(cls, limit: int | None = Query(PAGE_SIZE), offset: int = Query(0)) -> Self:
        logger.debug(f'Pagination.from_query({limit=}, {offset=})')
        return cls(limit=limit, offset=offset)


def select_more_f_q(stmt, pagination: Pagination = Depends(Pagination.from_query)):
    if pagination.offset:
        stmt = stmt.offset(pagination.offset)
    if pagination.limit:
        stmt = stmt.limit(pagination.limit + 1)
    return stmt


async def select_page_more(session, sqlselect, pagination: Pagination) -> tuple[list, bool]:
    if pagination.offset:
        sqlselect = sqlselect.offset(pagination.offset)
    if pagination.limit:
        sqlselect = sqlselect.limit(pagination.limit + 1)
    res = session.exec(sqlselect).all()
    more = len(res) > pagination.limit if pagination.limit else False
    return res[: pagination.limit], more


def search_column_stmt(model: type[SQLModel], column: str | None, search_str: str | None = None):
    if not column or not search_str:
        return select(model)
    search_ = f'%{search_str}%'
    colly = getattr(model, column)
    stmt = select(model).where(colly.ilike(search_))
    return stmt


async def model_type_from_path(category: str = Path(...)) -> type[SQLModel]:
    match category:
        case 'hire':
            return AmherstHireDB
        case 'sale':
            return AmherstSaleDB
        case 'customer':
            return AmherstCustomerDB


async def template_name_from_path(category: str = Path(...)):
    match category.title():
        case 'Hire' | 'Sale':
            return 'orders.html'
        case 'Customer':
            return 'customers.html'
        case _:
            raise ValueError(f'No template for {category}')


async def amrecs_from_query(
        category: type[SQLModel] = Depends(model_type_from_path),
        column: str = Query(None),
        q: str = Query(None),
        session: Session = Depends(get_session),
        pagination: Pagination = Depends(Pagination.from_query),
) -> list[AMHERST_TABLE_TYPES]:
    stmt = search_column_stmt(category, column, q)
    page, more = await select_page_more(session, stmt, pagination)
    logger.info(
        f'returned {len(page)} {category.__name__} records with {column} = {q}. (There are{' no' if not more else ''} more)'
    )
    if not page:
        raise HTTPException(status_code=404, detail=f'No records found for {q}')
    return page


async def query_stmt_multi(
        category: type[SQLModel] = Depends(model_type_from_path),
        queries: dict[str, str] | None = Body(...),
        logic_operator: str = Body('and', regex='^(and|or)$')
) -> select:
    filters = (
        [getattr(category, colname).ilike(f'%{val}%') for colname, val in queries.items()] if queries else []
    )
    if logic_operator == 'and':
        stmt = select(category).where(and_(*filters))
    else:
        stmt = select(category).where(or_(*filters))
    return stmt


async def amrecs_from_queries_multi(
        stmt: select = Depends(query_stmt_multi),
        session: Session = Depends(get_session),
        pagination: Pagination = Depends(Pagination.from_query),
):
    page, more = await select_page_more(session, stmt, pagination)
    return page




##


async def query_filters(
        category: type[SQLModel] = Depends(model_type_from_path),
        queries: dict[str, str] | None = Body(None),
) -> select:
    return [getattr(category, colname).ilike(f'%{val}%') for colname, val in queries.items()] if queries else []


async def stmt_from_q(
        filters: select = Depends(query_filters),
        category: type[SQLModel] = Depends(model_type_from_path),
        logic_operator: str = Body('and', regex='^(and|or)$')
) -> select:
    stmt = select(category)
    if filters:
        match logic_operator:
            case 'and':
                stmt = stmt.where(and_(*filters))
            case 'or':
                stmt = stmt.where(or_(*filters))

    return stmt


async def get_them(
        stmt: select = Depends(stmt_from_q),
        session: Session = Depends(get_session),
        pagination: Pagination = Depends(Pagination.from_query),
) -> tuple[list[AMHERST_TABLE_TYPES], bool]:
    return await select_page_more(session, stmt, pagination)
