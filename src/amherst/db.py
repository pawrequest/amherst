from __future__ import annotations

import contextlib
import functools
from typing import NamedTuple, Self

import sqlalchemy as sqa
import sqlmodel as sqm
from comtypes import CoInitialize, CoUninitialize
from fastapi import Depends, Path, Query
from loguru import logger

from amherst.config import settings
from amherst.filters import initial_filter
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


async def get_pyc(
        csrname: str = Path(...),
) -> PyCommence:
    CoInitialize()
    pyc = PyCommence.with_csr(csrname, filter_array=initial_filter(csrname))
    yield pyc
    CoUninitialize()


async def get_rows_contain_pk(
        pycmc: PyCommence = Depends(get_pyc),
        csrname: str = Path(...),
        pk_value: str = Path(...),

):
    csr = pycmc.csr(csrname)
    return csr.read_rows_pk_contains(pk_value)


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

##
