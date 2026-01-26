from pathlib import Path

import dotenv

envs_index = Path(r'C:\prdev\envs\sandbox.env')
dotenv.load_dotenv(envs_index)

from datetime import date, timedelta

import pytest

from amherst.models.amherst_models import AmherstCustomer

from pycommence import pycommence_context

# from pycommence.pycmc_types import RowData

TEST_DATE = date.today() + timedelta(days=2)
if TEST_DATE.weekday() in (5, 6):
    TEST_DATE += timedelta(days=7 - TEST_DATE.weekday())


@pytest.fixture(scope='session')
def amherst_customer() -> AmherstCustomer:
    with pycommence_context('Customer') as cmc:
        return cmc.read_row(pk='Test')
