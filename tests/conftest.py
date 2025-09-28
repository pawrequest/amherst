import os
from pathlib import Path
from amherst.set_env import set_env_files

set_env_files(Path(r'C:\prdev\envs\sandbox'))

from datetime import date, timedelta

import pytest

from amherst.models.amherst_models import AmherstHire, AmherstCustomer

from pycommence import pycommence_context
from pycommence.pycmc_types import RowData

TEST_DATE = date.today() + timedelta(days=2)
if TEST_DATE.weekday() in (5, 6):
    TEST_DATE += timedelta(days=7 - TEST_DATE.weekday())

@pytest.fixture(scope='session')
def amherst_customer_data() -> RowData:
    with pycommence_context(csrname='Customer') as cmc:
        return cmc.read_row(pk='Test')


@pytest.fixture(scope='session')
def amherst_customer(amherst_customer_data) -> AmherstCustomer:
    return AmherstCustomer(row_info=amherst_customer_data.row_info, **amherst_customer_data.data)




