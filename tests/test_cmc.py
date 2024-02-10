from amherst.models.hire import Hire
from amherst.models.hire_cmc import HireCmc
from amherst.models.sale import Sale
from amherst.models.shared import HireStatusEnum
from pycommence import CmcDB
import pytest
test_hire_name = 'Test - 10/11/2023 ref 42744'
test_sale_name = 'Test - 2/10/2024 ref 784'

@pytest.fixture()
def cmcdb():
    cmcdb = CmcDB()
    db_name = cmcdb.name
    if db_name != 'Radios_TEST':
        raise AssertionError('Database name is not Radios_TEST')
    return cmcdb



def test_from_cmc(cmcdb):
    cursor = cmcdb.get_cursor('Hire')
    ahire = cursor.get_record_one(test_hire_name)
    hirecmc = HireCmc(**ahire)
    hire = Hire.from_cmc(hirecmc)
    assert isinstance(hire, Hire)




def test_hire_from_name():
    hire2 = Hire.from_name(test_hire_name)
    assert isinstance(hire2, Hire)
    ...


def test_sale_from_name():
    sale = Sale.from_name(test_sale_name)
    assert isinstance(sale, Sale)

def test_current_hire(cmcdb):
    cursor = cmcdb.get_cursor('Hire')
    cursor.filter_by_field('Status', 'Equal To', 'Booked In')
    cursor.filter_by_field('Send Out Date', 'After, Last Week', fslot=2)
    cursor.filter_by_field('Closed', 'No', fslot=3)


    recs = cursor.get_records()
    for rec in recs:
        hire = Hire.from_record(rec)
        assert hire.status.status == HireStatusEnum.BOOKED_IN
        assert not hire.status.closed
        # if rec['Send Out Date']:
        #     assert rec['Send Out Date'] > '2022-01-01'
    ...