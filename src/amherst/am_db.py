from __future__ import annotations

import contextlib
import functools

import httpx
import sqlalchemy as sqa
import sqlmodel as sqm
from loguru import logger

from shipaw import ELClient
from amherst.am_config import am_sett
from amherst.models.am_record import AmherstRecord
from shipaw.models.pf_models import AddressTemporary
from shipaw.models.pf_shipment import ShipmentRequest


@functools.lru_cache(maxsize=1)
def get_engine() -> sqa.engine.base.Engine:
    connect_args = {'check_same_thread': False}
    return sqa.create_engine(am_sett().db_url, echo=False, connect_args=connect_args)


def get_session(engine=None) -> sqm.Session:
    if engine is None:
        engine = get_engine()
    with sqm.Session(engine) as session:
        yield session
    session.close()


@contextlib.contextmanager
def get_session_cm(engine=None):
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


def split_reference_numbers(am_record):
    customer_str = am_record.customer
    reference_numbers = {}

    for i in range(1, 6):
        start_index = (i - 1) * 24
        end_index = i * 24
        if start_index < len(customer_str):
            reference_numbers[f'reference_number{i}'] = customer_str[start_index:end_index]
        else:
            break

    return reference_numbers


def amherst_shipment_request(
        am_record: AmherstRecord,
        el_client: ELClient or None = None
) -> ShipmentRequest:
    el_client = el_client or ELClient()
    ref_nums = split_reference_numbers(am_record)
    try:
        chosen_address = el_client.choose_address(am_record.input_address())
    except Exception as e:
        logger.exception(e)
        chosen_address = AddressTemporary.model_validate(
            am_record.input_address(),
            from_attributes=True
        )
    return ShipmentRequest(
        recipient_contact=am_record.contact(),
        recipient_address=chosen_address,
        shipping_date=am_record.send_date,
        total_number_of_parcels=am_record.boxes,
        **ref_nums,
    )
