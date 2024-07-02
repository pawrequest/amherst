from __future__ import annotations

import contextlib
import functools
from datetime import date, datetime
from typing import NamedTuple, Self

import httpx
import sqlalchemy as sqa
import sqlmodel as sqm
from comtypes import CoInitialize, CoUninitialize
from fastapi import Query
from loguru import logger
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, col, select

from amherst.commence_adaptors import initial_filter
from amherst.config import settings
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


def get_pycmc() -> PyCommence:
    CoInitialize()
    pyc = PyCommence()
    pyc.set_csr('Hire')
    pyc.set_csr('Sale')
    pyc.set_csr('Customer')
    for cat in ['Hire', 'Sale', 'Customer']:
        [pyc.filter_cursor(initial_filter(cat), csrname=cat)]
    CoUninitialize()
    return pyc


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


async def select_page_more(session, sqlselect, pagination: Pagination) -> tuple[list, bool]:
    if pagination.offset:
        sqlselect = sqlselect.offset(pagination.offset)
    if pagination.limit:
        sqlselect = sqlselect.limit(pagination.limit + 1)
    res = session.exec(sqlselect).all()
    more = len(res) > pagination.limit if pagination.limit else False
    return res[: pagination.limit], more


def ordinal(n):
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def dt_ordinal(dt: datetime | date) -> str:
    return dt.strftime('%a {th} %b %Y').replace('{th}', ordinal(dt.day))


async def search_column_stmt1(table: type[SQLModel], column: str, search_str: str):
    search = f'%{search_str}%'
    colly = getattr(table, column)
    return select(table).where(col(colly).ilike(search))


def search_column_stmt(model, column: str | None, search_str: str | None = None):
    if not column or not search_str:
        return select(model)
    search_ = f'%{search_str}%'
    colly = getattr(model, column)
    stmt = select(model).where(colly.ilike(search_))
    return stmt
