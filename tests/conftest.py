import pytest

from pycommence import Cmc


@pytest.fixture
def cmc_db():
    yield Cmc()


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
    return hire_csr.get_record(hire_name)


@pytest.fixture
def sale_rec(sale_csr):
    sale_name = 'Test - 18/08/2023 ref 450'
    return sale_csr.get_record(sale_name)