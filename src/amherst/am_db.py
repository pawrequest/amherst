from __future__ import annotations

import httpx
import sqlalchemy as sqa
import sqlmodel as sqm
from dotenv import load_dotenv
from loguru import logger

from amherst import shipper
from pycommence import csr_context

load_dotenv()
# DB_URL = 'sqlite:///:memory:'
DB_URL = "sqlite:///amherst.db"
CONNECT_ARGS = {'check_same_thread': False}
ENGINE = sqa.create_engine(DB_URL, echo=False, connect_args=CONNECT_ARGS)


def engine_config():
    return {'db_url': DB_URL, 'connect_args': CONNECT_ARGS}


def get_session(engine=None) -> sqm.Session:
    if engine is None:
        engine = ENGINE
    with sqm.Session(engine) as session:
        yield session
    session.close()


def get_pfc():
    try:
        return shipper.AmShipper.from_env()
    except Exception as e:
        logger.error(f'get_pfc: {e}')


async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client


def create_db(engine=None):
    if engine is None:
        engine = ENGINE
    sqm.SQLModel.metadata.create_all(engine)


def get_hire_cursor():
    with csr_context('Hire') as cursor:
        yield cursor
