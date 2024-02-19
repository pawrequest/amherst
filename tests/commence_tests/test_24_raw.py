import pytest

from amherst.models import Hire, HireCmc, Sale, SaleCmc
from pycommence import Csr, api_funcs as api
from pycommence.wrapper.cmc_cursor import CsrCmc

"""NO CHECKS ON DATABASE NAME!!"""


def test_csr(hire_csr):
    assert isinstance(hire_csr, Csr)


def test_hire_csr(hire_csr):
    assert isinstance(hire_csr, Csr)


def test_sale_csr(sale_csr):
    assert isinstance(sale_csr, Csr)


def test_hire_cmc(hire_cmc):
    assert isinstance(hire_cmc, HireCmc)


def test_sale_cmc(sale_cmc):
    assert isinstance(sale_cmc, SaleCmc)


def test_hire_from_cmc(hire_cmc):
    hire = Hire.from_cmc(hire_cmc)
    assert isinstance(hire, Hire)
    # hire_dates = submodel_from_cmc(HireDates, hire_cmc)
    # h2 = hire_cmc.submodel(HireDates)
    # assert isinstance(hire_dates, HireDates)
    # assert isinstance(h2, HireDates)


def test_sale_from_cmc(sale_cmc):
    sale = Sale.from_cmc(sale_cmc)
    assert isinstance(sale, Sale)


@pytest.mark.xfail(reason='Not implemented')
def test_dates_after(hire_csr: CsrCmc):
    api.filter_by_field(hire_csr, 'Send Out Date', 'Before', 'today')
    res = api.get_all_records(hire_csr)
    one_hire_cmc = HireCmc.model_validate(res[0])
    one_hire = Hire.from_cmc(one_hire_cmc)
    assert isinstance(one_hire, Hire)
