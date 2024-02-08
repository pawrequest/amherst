import pytest

from pycommence.wrapper.cmc_cursor import CmcCursor
from pycommence.wrapper.cmc_db_24 import CmcConnection
from pycommence import api


@pytest.fixture
def cmc_db():
    yield CmcConnection()


@pytest.fixture
def new_cursor(cmc_db):
    def new_curs():
        return cmc_db.get_cursor('Hire')

    return new_curs()


def test_csr(new_cursor):
    assert isinstance(new_cursor, CmcCursor)


