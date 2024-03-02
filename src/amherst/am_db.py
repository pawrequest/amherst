from __future__ import annotations

import httpx
from dotenv import load_dotenv
from loguru import logger
import sqlmodel as sqm
import sqlalchemy as sqa

from pycommence import csr_context
from amherst import shipper

load_dotenv()
DB_URL = "sqlite:///:memory:"
# DB_URL = "sqlite:///amherst.db"
CONNECT_ARGS = {"check_same_thread": False}
ENGINE = sqa.create_engine(DB_URL, echo=False, connect_args=CONNECT_ARGS)


def engine_config():
    return {"db_url": DB_URL, "connect_args": CONNECT_ARGS}


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
        logger.error(f"get_pfc: {e}")


async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client


def create_db(engine=None):
    if engine is None:
        engine = ENGINE
    sqm.SQLModel.metadata.create_all(engine)


def get_hire_cursor():
    with csr_context() as cursor:
        yield cursor
