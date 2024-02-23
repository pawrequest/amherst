from amherst.models import Hire, Sale
from pycommence import Csr

"""NO CHECKS ON DATABASE NAME!!"""


def test_csr(hire_csr):
    assert isinstance(hire_csr, Csr)


def test_hire_csr(hire_csr):
    assert isinstance(hire_csr, Csr)


def test_sale_csr(sale_csr):
    assert isinstance(sale_csr, Csr)


def test_salwe_fxt(sale_fxt):
    assert isinstance(sale_fxt, Sale)


def test_hire_fxt(hire_fxt):
    assert isinstance(hire_fxt, Hire)

# @pytest.mark.xfail(reason='Not implemented')
# def test_dates_after(hire_csr: CsrCmc):
#     api.filter_by_field(hire_csr, 'Send Out Date', 'Before', 'today')
#     res = api.get_all_records(hire_csr)
#     one_hire_cmc = HireCmc.model_validate(res[0])
#     one_hire = Hire.from_cmc(one_hire_cmc)
#     assert isinstance(one_hire, Hire)
