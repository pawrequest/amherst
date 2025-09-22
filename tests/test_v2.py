from pycommence.pycmc_types import RowData

from amherst.models.amherst_models import AmherstHire


def test_amherst_hire(amherst_hire_data: RowData):
    info = amherst_hire_data.row_info
    hire = amherst_hire_data.data
    res = AmherstHire(row_info=info, **hire)
    res = res.model_validate(res)
    assert res.name == 'TEST RECORD DO NOT EDIT'

