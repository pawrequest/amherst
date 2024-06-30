from __future__ import annotations

import contextlib
import functools

import httpx
import sqlalchemy as sqa
import sqlmodel as sqm
from loguru import logger

from amherst.config import settings
from pycommence.pycommence_v2 import PyCommence
from shipaw.expresslink_client import ELClient


@functools.lru_cache(maxsize=1)
def get_engine() -> sqa.engine.base.Engine:
    connect_args = {'check_same_thread': False}
    return sqa.create_engine(settings().db_url, echo=False, connect_args=connect_args)


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


def get_a_pycmc(csrname: str):
    return PyCommence.with_csr(csrname=csrname)


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
