import pytest

from amherst.models.hire_in import HireIn, INITIAL_FILTER_ARRAY
from amherst.models.hire_raw import HireRaw
from amherst.models.sale import Sale
from amherst.models.shared import HireStatusEnum
from pycommence import Cmc, Csr
from pycommence.wrapper.cmc_db import get_csr

TEST_HIRE_NAME1 = 'test - 10/11/2023 ref 42744'
TEST_SALE_NAME1 = 'test - 2/10/2024 ref 784'
TEST_SALE_NAME = 'Test - 18/08/2023 ref 450'
TEST_HIRE_NAME = "Test - 16/08/2023 ref 31619"


@pytest.fixture()
def cmc():
    cmc = Cmc()
    # db_name = cmc.name
    # if db_name != 'Radios_TEST':
    #     raise AssertionError('Database name is not Radios_TEST')
    return cmc


def test_csr(hire_csr):
    assert isinstance(hire_csr, Csr)


def test_default_csr():
    csr = get_csr('Hire')
    assert csr._cursor.category == 'Hire'


def test_from_cmc(cmc):
    csr = cmc.get_cursor('Hire')
    ahire = csr.get_record(TEST_HIRE_NAME)
    hirecmc = HireRaw(**ahire)
    hire = HireIn.from_raw_cmc(hirecmc)
    assert isinstance(hire, HireIn)


def test_hire_from_name():
    hire2 = HireIn.from_name(TEST_HIRE_NAME)
    assert isinstance(hire2, HireIn)
    ...


def test_sale_from_name():
    sale = Sale.from_name(TEST_SALE_NAME)
    assert isinstance(sale, Sale)


def test_current_hire(cmc):
    cursor = cmc.get_cursor('Hire')
    cursor.filter_by_field('Status', 'Equal To', 'Booked In')
    cursor.filter_by_field('Send Out Date', 'After, Last Week', fslot=2)
    cursor.filter_by_field('Closed', 'No', fslot=3)

    recs = cursor.get_all_records()
    for rec in recs:
        hire = HireIn.from_record(rec)
        assert hire.hire_status.status == HireStatusEnum.BOOKED_IN
        assert not hire.hire_status.closed
        # if rec['Send Out Date']:
        #     assert rec['Send Out Date'] > '2022-01-01'
    ...


def test_filter(cmc):
    csr = get_csr('Hire')
    fil = INITIAL_FILTER_ARRAY
    csr.filter_by_array(fil)
    recs = csr.get_all_records()
    for rec in recs:
        hire = HireIn.from_record(rec)
        assert hire.hire_status.status == HireStatusEnum.BOOKED_IN
    print(len(recs))
