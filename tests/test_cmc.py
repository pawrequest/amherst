import pytest

from amherst.models.hire import Hire
from amherst.models.hire_cmc import HireCmc
from amherst.models.sale import Sale
from amherst.models.shared import HireStatusEnum
from pycommence import Cmc
from pycommence.filters import CmcFilter, FilterCondition
from pycommence.wrapper.cmc_db import get_csr

TEST_HIRE_NAME = 'test - 10/11/2023 ref 42744'
TEST_SALE_NAME = 'test - 2/10/2024 ref 784'


@pytest.fixture()
def cmc():
    cmc = Cmc()
    db_name = cmc.name
    if db_name != 'Radios_TEST':
        raise AssertionError('Database name is not Radios_TEST')
    return cmc


def test_default_csr():
    csr = get_csr('Hire')
    assert csr._cursor.category == 'Hire'


def test_from_cmc(cmc):
    csr = cmc.get_cursor('Hire')
    ahire = csr.get_record(TEST_HIRE_NAME)
    hirecmc = HireCmc(**ahire)
    hire = Hire.from_cmc(hirecmc)
    assert isinstance(hire, Hire)


def test_hire_from_name():
    hire2 = Hire.from_name(TEST_HIRE_NAME)
    assert isinstance(hire2, Hire)
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
        hire = Hire.from_record(rec)
        assert hire.status.status == HireStatusEnum.BOOKED_IN
        assert not hire.status.closed
        # if rec['Send Out Date']:
        #     assert rec['Send Out Date'] > '2022-01-01'
    ...


def test_filter(cmc):
    csr = get_csr('Hire')

    cmc_filter = CmcFilter(
        field_name='Status',
        condition=FilterCondition.EQUAL_TO,
        value=HireStatusEnum.BOOKED_IN,
        slot=1
    )
    csr.filter(cmc_filter)

    # cmc_filter2 = CmcFilter(
    #     field_name='Status',
    #     condition=FilterCondition.EQUAL_TO,
    #     value=HireStatusEnum.PACKED,
    #     slot=2
    # )
    # csr.filter(cmc_filter2)

    cmc_filter3 = CmcFilter(
        field_name='Send Out Date',
        condition=FilterCondition.AFTER,
        value='Last Week',
        slot=3
    )
    csr.filter(cmc_filter3)
    # csr._cursor.set_filter_logic('OR, AND, AND')
    recs = csr.get_all_records()
    for rec in recs:
        hire = Hire.from_record(rec)
        assert hire.status.status == HireStatusEnum.BOOKED_IN
    print(len(recs))

