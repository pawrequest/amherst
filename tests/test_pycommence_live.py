import random

import pytest
import pytest_asyncio
from amherst.commence import initial_filter
from amherst.importer import amrec_to_booking, cmc_record_to_amrec
from amherst.models.am_record import AmherstRecord
from loguru import logger
from pycommence import PyCommence


@pytest.fixture(
    params=['Hire', 'Sale'],
)
def pycmc(request) -> PyCommence:
    table = request.param
    with PyCommence.from_table_name_context(table, filter_array=initial_filter(table)) as cmc:
        logger.warning(f'testing {cmc.row_count} {table} records')
        yield cmc


@pytest.fixture
def random_record(pycmc):
    records = pycmc.records()
    logger.warning(f'there are {len(records)} records')
    assert records
    return random.choice(records)


@pytest_asyncio.fixture
async def random_amrec(pycmc) -> AmherstRecord:
    record = random.choice(pycmc.records())
    logger.info(f'testing {record["Name"]}')
    record['cmc_table_name'] = pycmc.csr.category
    amrec = await cmc_record_to_amrec(record)
    return amrec


@pytest_asyncio.fixture
async def random_booking(random_amrec):
    return await amrec_to_booking(random_amrec)


@pytest_asyncio.fixture
async def random_booking_in_db(random_booking, test_session_fxt):
    booking = random_booking
    test_session_fxt.add(booking)
    test_session_fxt.commit()
    test_session_fxt.refresh(booking)
    assert booking.id
    return booking


@pytest.mark.parametrize('run', range(5))  # Run the test 5 times
@pytest.mark.asyncio
async def test_random_record_to_booking(random_booking_in_db, run):
    print(f'run {run}')
    assert random_booking_in_db
    assert random_booking_in_db.id
