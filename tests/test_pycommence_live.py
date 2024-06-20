import random

import pytest
import pytest_asyncio
from loguru import logger

from amherst.commence import initial_filter
from amherst.importer import amrec_to_booking, cmc_record_to_amrec
from amherst.models.am_record import AmherstRecord
from amherst.models.db_models import BookingStateDB
from pycommence import PyCommence
from .test_pycommence_mock import FAKE_EMAIL, FAKE_PHONE


@pytest.fixture(
    params=['Hire', 'Sale'],
)
def pycmc(request) -> PyCommence:
    table = request.param
    with PyCommence.from_table_name_context(table, filter_array=initial_filter(table)) as cmc:
        logger.info(f'testing against {cmc.row_count} {table} records')
        yield cmc


@pytest_asyncio.fixture
async def random_amrec(pycmc) -> AmherstRecord:
    record = random.choice(pycmc.records())
    logger.info(f'testing {record["Name"]}')
    record['cmc_table_name'] = pycmc.csr.category
    amrec = await cmc_record_to_amrec(record)
    amrec.telephone = FAKE_PHONE
    amrec.email = FAKE_EMAIL
    return amrec


@pytest_asyncio.fixture
async def random_booking(random_amrec: AmherstRecord):
    return await amrec_to_booking(random_amrec)


@pytest_asyncio.fixture
async def random_booking_in_db(random_booking: BookingStateDB, test_session_fxt):
    booking = random_booking
    test_session_fxt.add(booking)
    test_session_fxt.commit()
    test_session_fxt.refresh(booking)
    assert booking.id
    return booking


@pytest.mark.parametrize('run', range(5))
@pytest.mark.asyncio
async def test_random_record_to_booking(random_booking_in_db: BookingStateDB, run):
    print(f'run {run}')
    assert random_booking_in_db
    assert random_booking_in_db.id
