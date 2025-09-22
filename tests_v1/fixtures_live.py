import random

import pytest
import pytest_asyncio
from loguru import logger
from pycommence.pycommence import PyCommence

from .fixtures_mock import FAKE_EMAIL, FAKE_PHONE


@pytest.fixture(
    params=['Hire', 'Sale'],
)
def pycmc(request) -> PyCommence:
    table = request.param
    with PyCommence.with_csr(table, filter_array=initial_filter(table)) as cmc:
        logger.info(f'testing against {cmc.row_count} {table} records')
        yield cmc


@pytest_asyncio.fixture
async def random_amrec(pycmc) -> AmherstRecord:
    record = random.choice(pycmc.records())
    logger.info(f'testing {record["Name"]}')
    record['category'] = pycmc.csr().category
    amrec = await cmc_record_to_amrec(record)
    amrec.telephone = FAKE_PHONE
    amrec.delivery_contact_email = FAKE_EMAIL
    return amrec


@pytest_asyncio.fixture
async def random_booking(random_amrec: AmherstRecord) -> BookingStateDB:
    return await amrec_to_booking(random_amrec)


@pytest_asyncio.fixture
async def random_booking_in_db(random_booking: BookingStateDB, test_session_fxt):
    booking = random_booking
    test_session_fxt.add(booking)
    test_session_fxt.commit()
    test_session_fxt.refresh(booking)
    assert booking.id
    return booking
