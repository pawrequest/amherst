import pytest

from amherst.models.am_record import AmherstRecord
from pycommence.cursor import get_csr
from pycommence.pycmc_types import CmcFilter, FilterArray
from pycommence import PyCommence


@pytest.fixture
def pycmc():
    csr = get_csr('Hire')
    yield PyCommence(csr=csr)


def test_pycmc(pycmc):
    assert isinstance(pycmc, PyCommence)


def test_get_records_by_field(pycmc: PyCommence):
    res = pycmc.records_by_field('Name', 'Test Customer - 2/21/2024 ref 43383')
    assert isinstance(res, list)
    assert isinstance(res[0], dict)
    assert res[0]['firstName'] == 'Jeff'


def test_shipable(hire_record_fxt):
    shipa = AmherstRecord.model_validate(hire_record_fxt)


@pytest.fixture
def fil1():
    return CmcFilter(
        cmc_col='Status',
        condition='Equal To',
        value='Booked In',
    )


@pytest.fixture
def fil_array(fil1):
    fil_array = FilterArray(filters={1: fil1})
    assert isinstance(fil_array, FilterArray)
    assert fil_array.filters[1] == fil1
    return fil_array


def test_fiters(pycmc_radios_hire, fil_array):
    count = pycmc_radios_hire.csr.row_count
    with pycmc_radios_hire.csr.temporary_filter_by_array(fil_array):
        c2 = pycmc_radios_hire.csr.row_count
        assert c2 > count
        ...
