from amherst.models.hire import Hire
from amherst.models.hire_cmc import HireCmc
from pycommence import CmcDB
import pytest
test_hire_name = 'Test - 10/11/2023 ref 42744'
test_sale_name = 'Test - 05/10/2023 ref 461'

@pytest.fixture()
def cmcdb():
    cmcdb = CmcDB()
    db_name = cmcdb.name
    if db_name != 'Radios_TEST':
        raise AssertionError('Database name is not Radios_TEST')
    return cmcdb



def test_from_cmc(cmcdb):
    cursor = cmcdb.get_cursor('Hire')
    ahire = cursor.get_record(test_hire_name)
    hirecmc = HireCmc(**ahire)
    hire = Hire.from_cmc(hirecmc)
    assert isinstance(hire, Hire)




def test_hire_from_name():
    hire2 = Hire.from_name(test_hire_name)
    assert isinstance(hire2, Hire)
    ...
