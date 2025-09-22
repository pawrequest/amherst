import os

os.environ['AMHERSTPR'] = r'C:\prdev\envs\sandbox'

from amherst.set_env import set_amherstpr_env

set_amherstpr_env(sandbox=True)

from datetime import date, timedelta

import pytest

from amherst.models.amherst_models import AmherstHire

from pycommence import pycommence_context
from pycommence.pycmc_types import RowData

TEST_DATE = date.today() + timedelta(days=2)
if TEST_DATE.weekday() in (5, 6):
    TEST_DATE += timedelta(days=7 - TEST_DATE.weekday())


@pytest.fixture(scope='session')
def amherst_hire_data() -> RowData:
    with pycommence_context(csrname='Hire') as cmc:
        return cmc.read_row(pk='TEST RECORD DO NOT EDIT')


@pytest.fixture(scope='session')
def amherst_hire(amherst_hire_data) -> AmherstHire:
    return AmherstHire(row_info=amherst_hire_data.row_info, **amherst_hire_data.data)




