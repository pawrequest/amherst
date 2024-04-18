from __future__ import annotations

import functools
import os
from contextlib import contextmanager

import httpx
import pydantic as _p
import sqlalchemy as sqa
import sqlmodel as sqm
from loguru import logger

from amherst import am_config, am_types, rec_importer, shipper
from amherst.models import shipable_item
from shipaw import pf_config


@functools.lru_cache(maxsize=1)
def get_engine() -> sqa.engine.base.Engine:
    pf_sett = pf_config.PF_SETTINGS
    am_sett = am_config.AM_SETTINGS

    db_name = f'{str(am_sett.db_loc)}{'' if pf_sett.ship_live else "_test"}'
    db_url = f'sqlite:///{db_name}'
    logger.info(f'DB_URL: {db_url}')
    connect_args = {'check_same_thread': False}
    return sqa.create_engine(db_url, echo=False, connect_args=connect_args)


def get_session(engine=None) -> sqm.Session:
    if engine is None:
        engine = get_engine()
    with sqm.Session(engine) as session:
        yield session
    session.close()


def get_el_client():
    try:
        return shipper.AmShipper.from_pyd()
    except Exception as e:
        logger.error(f'get_pfc: {e}')


@contextmanager
def el_context():
    try:
        pfc_instance = shipper.AmShipper.from_pyd()
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


def record_to_manager(category: am_types.AmherstTableName, record) -> int:
    """Add Commence data to the database.

    Convert a record from a Commence table to a :class:shipable_item.ShipableItem
    Add item to a new :class:managers.BookingManagerDB
    Commit manager to sql.

    Args:
        category (str): Commence table name
        record (dict): Commence record

    Returns:
        int: Manager id
    """
    pf_shipper = shipper.AmShipper.from_pyd()
    with sqm.Session(get_engine()) as session:
        item = shipable_item.ShipableItem(cmc_table_name=category, record=record)
        manager = rec_importer.item_to_manager(item, pfcom=pf_shipper)
        session.add(manager)
        session.commit()
        return manager.id
