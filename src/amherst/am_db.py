from __future__ import annotations

import pathlib

import httpx
import sqlalchemy as sqa
import sqlmodel as sqm
from dotenv import load_dotenv
from loguru import logger
from pycommence.api import csr_context

from amherst import shipper

load_dotenv()
db_name = 'amherst.db'
DB_URL = f"sqlite:///{db_name}"

# DB_URL = 'sqlite:///:memory:'
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


def destroy_db(engine=None):
    if engine is None:
        engine = ENGINE
    sqm.SQLModel.metadata.drop_all(engine)

    # db_path = pathlib.Path(db_name)
    # db_path.unlink(missing_ok=True)

def get_hire_cursor():
    with csr_context('Hire') as cursor:
        yield cursor
