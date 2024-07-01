from __future__ import annotations

import contextlib
import functools
from datetime import date, datetime
from typing import NamedTuple

import httpx
import sqlalchemy as sqa
import sqlmodel
import sqlmodel as sqm
from comtypes import CoInitialize, CoUninitialize
from fastapi import Query
from loguru import logger
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, col, select

from amherst.commence_adaptors import initial_filter
from amherst.config import settings
from amherst.models.am_record_smpl import AmherstTableDB
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


PAGE_SIZE = 10


def get_pagination(limit: int = Query(PAGE_SIZE, gt=0), offset: int = Query(0, ge=0)):
    return Pagination(limit=limit, offset=offset)


class Pagination(NamedTuple):
    limit: int
    offset: int


async def select_page_more(session, sqlselect, pagination: Pagination) -> tuple[list, bool]:
    stmt = sqlselect.offset(pagination.offset).limit(pagination.limit + 1)
    res = session.exec(stmt).all()
    more = len(res) > pagination.limit
    return res[: pagination.limit], more


def ordinal(n):
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def dt_ordinal(dt: datetime | date) -> str:
    return dt.strftime('%a {th} %b %Y').replace('{th}', ordinal(dt.day))


async def search_column(table, column, search_str: str):
    search = f'%{search_str}%'
    return select(table).where(col(column).ilike(search))


