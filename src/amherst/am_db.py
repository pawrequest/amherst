from __future__ import annotations

import functools
import os
from contextlib import contextmanager

import httpx
import pydantic as _p
import sqlalchemy as sqa
import sqlmodel as sqm
# from dotenv import load_dotenv
from loguru import logger

from amherst import rec_importer, shipper
from amherst.models import hire_model, managers


# db_name = os.environ.get('DB_LOC')
# db_name = os.environ.get('DB_LOC', 'amherst.db')
# DB_URL = f'sqlite:///{db_name}'
# logger.info(f'DB_URL: {DB_URL}')
#
# # DB_URL = 'sqlite:///:memory:'
# CONNECT_ARGS = {'check_same_thread': False}
# ENGINE = sqa.create_engine(DB_URL, echo=False, connect_args=CONNECT_ARGS)

@functools.lru_cache(maxsize=1)
def get_engine():
    db_name = os.environ.get('DB_LOC', 'amherst.db')
    DB_URL = f'sqlite:///{db_name}'
    # DB_URL = 'sqlite:///:memory:'
    logger.info(f'DB_URL: {DB_URL}')

    CONNECT_ARGS = {'check_same_thread': False}
    return sqa.create_engine(DB_URL, echo=False, connect_args=CONNECT_ARGS)


def get_session(engine=None) -> sqm.Session:
    if engine is None:
        engine = get_engine()
    with sqm.Session(engine) as session:
        yield session
    session.close()


def get_pfc():
    try:
        return shipper.AmShipper.from_env()
    except Exception as e:
        logger.error(f'get_pfc: {e}')


@contextmanager
def get_pfc_context():
    try:
        pfc_instance = shipper.AmShipper.from_env()
        yield pfc_instance
    except Exception as e:
        logger.error(f'get_pfc: {e}')
    finally:
        ...


async def get_http_client():
    async with httpx.AsyncClient() as client:
        yield client


def create_db(engine=None):
    if engine is None:
        engine = get_engine()
    sqm.SQLModel.metadata.create_all(engine)


def destroy_db(engine=None):
    if engine is None:
        engine = get_engine()
    sqm.SQLModel.metadata.drop_all(engine)

    # db_path = pathlib.Path(db_name)
    # db_path.unlink(missing_ok=True)


def delete_all_records(model_type: type[_p.BaseModel]):
    with sqm.Session(get_engine()) as session:
        statement = sqm.delete(model_type)
        session.execute(statement)
        session.commit()
        logger.info(f'{model_type.__name__} old records deleted')


def erasedb_add_record(category, record):
    pf_shipper = shipper.AmShipper.from_env()

    with sqm.Session(get_engine()) as session:
        delete_all_records(managers.BookingManagerDB)

        # delete_all_records(managers.BookingManagerDB)
        item = hire_model.ShipableItem(cmc_table_name=category, record=record)
        manager = rec_importer.generic_item_to_manager(item, pfcom=pf_shipper)
        session.add(manager)
        session.commit()
