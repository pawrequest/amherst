import pytest

from amherst.models.am_record import AmherstRecord
from pycommence.cursor import get_csr
from pycommence.pycmc_types import CmcError
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

def test_shipable(hire_record):
    shipa = AmherstRecord.model_validate(hire_record)