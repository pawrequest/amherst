from __future__ import annotations

from dotenv import load_dotenv
from loguru import logger
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session
from pydantic import json

from amherst.models import Hire, HireIn  # noqa: F401

from amherst.shipper import AmShipper
from pycommence import csr_context

load_dotenv()
DB_URL = "sqlite:///:memory:"
# DB_URL = "sqlite:///amherst.db"
CONNECT_ARGS = {"check_same_thread": False}
ENGINE = create_engine(DB_URL, echo=False, connect_args=CONNECT_ARGS, json_serializer=json.dumps)


def engine_config():
    return {"db_url": DB_URL, "connect_args": CONNECT_ARGS}


def get_session(engine=None) -> Session:
    if engine is None:
        engine = ENGINE
    with Session(engine) as session:
        yield session
    session.close()


def get_pfc():
    try:
        return AmShipper.from_env()
    except Exception as e:
        logger.error(f"get_pfc: {e}")


def create_db(engine=None):
    if engine is None:
        engine = ENGINE
    SQLModel.metadata.create_all(engine)


def get_hire_cursor():
    with csr_context() as cursor:
        yield cursor


def populate_db_from_cmc(session: Session):
    # data = hire_records
    with csr_context(Hire.cmc_table_name) as csr:
        filters = Hire.initial_filter_array.default
        data = csr.filter_by_array(filters, get=True)
    Hire.records_to_sesh(data, session)
