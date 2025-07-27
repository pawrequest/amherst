import functools

import pytest
from sqlalchemy import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from amherst.app import app
from amdev.bench.sql import get_session
from shipaw.expresslink_client import ELClient
from shipaw.pf_config import PFSandboxSettings, pf_sandbox_sett

DB_FILE = 'sqlite:///test.db'
DB_MEMORY = 'sqlite:///:memory:'


@functools.lru_cache(maxsize=1)
def get_test_session():
    engine = create_engine(
        DB_MEMORY,
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        # echo=True
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        try:
            return session
        finally:
            ...
            session.rollback()


def override_get_db():
    sesh = get_test_session()
    try:
        yield sesh
    finally:
        sesh.rollback()


app.dependency_overrides[get_session] = override_get_db


@pytest.fixture(scope='function')
def test_session_fxt():
    session = get_test_session()
    try:
        return session
    finally:
        session.rollback()


@pytest.fixture(scope='session')
def sett():
    settings = pf_sandbox_sett()
    PFSandboxSettings.model_validate(settings, from_attributes=True)
    yield settings


@pytest.fixture(scope='session')
def el_client(sett):
    yield ELClient(settings=sett)


# @pytest.mark.usefixtures('booking_mock', 'random_booking')
# @pytest_asyncio.fixture(
#     params=['booking_mock', 'random_booking'],
# )
# async def booking_fxt(request):
#     print(f'request.param: {request.param}')
#     booking = request.getfixturevalue(request.param)
#     yield booking


# __all__ = [
#     'test_session_fxt',
#     'sett',
#     'el_client',
#     'random_booking',
#     'random_booking',
#     'random_booking_in_db',
#     'random_booking',
#     'random_amrec',
#     'pycmc',
#     'contact_xmpl',
#     'address_xmpl',
#     'booking_mock_fxt',
#     'booking_mock_db',
#     'amrec_mock',
# ]
