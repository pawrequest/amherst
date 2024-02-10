import pytest

from pycommence import api
from pycommence.wrapper.cmc_db import CmcDB


@pytest.fixture
def cmc_db():
    yield CmcDB()


def new_curs(cmc_db, table_name: str):
    return cmc_db.get_cursor(table_name)


@pytest.fixture
def hire_csr(cmc_db):
    return new_curs(cmc_db, 'Hire')

@pytest.fixture
def sale_csr(cmc_db):
    return new_curs(cmc_db, 'Sale')

@pytest.fixture
def hire_rec(hire_csr):
    hire_name = 'Test - 16/08/2023 ref 31619'
    hire_rec = api.get_record(hire_csr, hire_name)
    return hire_rec


@pytest.fixture
def sale_rec(sale_csr):
    sale_name = 'Test - 18/08/2023 ref 450'
    sale_rec = api.get_record(sale_csr, sale_name)
    return sale_rec