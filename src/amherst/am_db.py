from __future__ import annotations

import functools

import httpx
import sqlalchemy as sqa
import sqlmodel as sqm
from loguru import logger
from shipaw import ELClient

from amherst.am_config import AM_SETTINGS
from amherst.models.am_record import AmherstRecord
from amherst.models.shipment_record import ShipmentRecordDB


@functools.lru_cache(maxsize=1)
def get_engine() -> sqa.engine.base.Engine:
    am_sett = AM_SETTINGS
    connect_args = {'check_same_thread': False}
    return sqa.create_engine(am_sett.db_url, echo=False, connect_args=connect_args)


def get_session(engine=None) -> sqm.Session:
    if engine is None:
        engine = get_engine()
    with sqm.Session(engine) as session:
        yield session
    session.close()


def get_el_client():
    try:
        return ELClient()
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


def amherst_record_to_shiprec(am_record: AmherstRecord) -> int:
    with sqm.Session(get_engine()) as session:
        initial_state = am_record.initial_shipment_state
        shiprec = ShipmentRecordDB(
            record=am_record,
            shipment=initial_state,
        )
        shiprec = shiprec.model_validate(shiprec)
        session.add(shiprec)
        session.commit()
        return shiprec.id
