import random
from pprint import pprint

import pytest
import pytest_asyncio
from loguru import logger
from starlette.testclient import TestClient

from amherst.commence_adaptors import initial_filter
from amherst.models.am_record_smpl import AmherstTableDB
from pycommence.pycommence_v2 import PyCommence
from shipaw.models.pf_shipment import Shipment
from shipaw.ship_types import ShipDirection
from .client import test_client  # noqa


@pytest.fixture(params=['Hire', 'Sale', 'Customer'])
def pycmc(request) -> PyCommence:
    """Fixture for PyCommence instance with a CSR of the parameterized tablename."""
    table = request.param
    cmc = PyCommence.with_csr(table, filter_array=initial_filter(table))
    logger.info(f'testing against {cmc.csr().row_count} {table} records')
    yield cmc


@pytest_asyncio.fixture(scope='function')
async def amrec(pycmc: PyCommence):
    """Fixture for a random AmherstTableDB record via validation with appropriate subclass of AmherstTable"""
    record = random.choice(list(pycmc.csr().rows(count=10)))
    logger.info(f'testing {record["Name"]}')
    record['category'] = pycmc.csr().category
    pprint(record)
    amrec = AmherstTableDB.from_dict(record)
    return amrec


@pytest.fixture(params=[ShipDirection.Inbound, ShipDirection.Outbound, ShipDirection.Dropoff])
def test_shipment(request, amrec):
    """Get a Shipment from the random fixture, parameterized for direction."""
    direction = request.param
    ship = amrec.to_shipment(direction=direction)
    ship.recipient_contact.notifications = None
    if ship.collection_info:
        ship.collection_info.collection_contact.notifications = None
    assert isinstance(ship, Shipment)
    assert not ship.recipient_contact.notifications
    if ship.collection_info:
        assert not ship.collection_info.collection_contact.notifications
    print('NOTIFICATIONS:', ship.notifications_str)
    return ship


def test_get_shipment(test_shipment: Shipment):
    """Test amrec and test_shipment fixtures. shows that importing random records yields valid Shipment instances."""
    assert isinstance(test_shipment, Shipment)


@pytest.fixture(scope='function')
def session_with_amrec(test_session_fxt, amrec):
    """Fixture for a test session with an AmherstTableDB record."""
    amrecdb = AmherstTableDB.model_validate(amrec, from_attributes=True)
    test_session_fxt.add(amrecdb)
    test_session_fxt.commit()
    test_session_fxt.refresh(amrecdb)
    try:
        yield test_session_fxt
    finally:
        test_session_fxt.delete(amrecdb)


@pytest.mark.parametrize('direction', [ShipDirection.Inbound, ShipDirection.Outbound, ShipDirection.Dropoff])
def test_get_shipment_api(test_client: TestClient, session_with_amrec, direction):
    arec = session_with_amrec.query(AmherstTableDB).first()
    resp = test_client.get(f'/api/get_shipment/{direction}/{arec.id}')
    ship = Shipment.model_validate(resp.json())
    ship = no_notifications(ship)
    assert isinstance(ship, Shipment)
    assert not any(
        [
            ship.recipient_contact.notifications,
            (ship.collection_info.collection_contact.notifications if ship.collection_info else None),
        ]
    )


def no_notifications(ship: Shipment):
    if ship.collection_info:
        ship.collection_info.collection_contact.notifications = None
    ship.recipient_contact.notifications = None
    return ship


def test_gererate_with_ids(pycmc):
    for rec in pycmc.csr().rows(with_id=True, count=10):
        assert isinstance(rec, dict)


def test_genids_add_sesh(test_session_fxt, pycmc):
    csrname = pycmc.csr().category
    for record in pycmc.csr().rows(with_id=True, count=10):
        record['category'] = csrname
        am_table_in = AmherstTableDB.from_dict(record)
        if indb := test_session_fxt.get(AmherstTableDB, am_table_in.id):
            [setattr(indb, k, v) for k, v in am_table_in.model_dump().items() if k not in ('row_id', 'category')]
        else:
            indb = AmherstTableDB(**am_table_in.model_dump())
        test_session_fxt.add(indb)
    test_session_fxt.commit()
