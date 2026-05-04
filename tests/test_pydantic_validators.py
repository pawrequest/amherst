from datetime import date, timedelta
from pathlib import Path

import dotenv
import pytest
from amherst_core.models import AmherstCustomer
from pycommence import PyCommence
from pycommence.core.row_data import RowData

envs_index = Path(r'C:\prdev\envs\sandbox.env')
dotenv.load_dotenv(envs_index)
TEST_DATE = date.today() + timedelta(days=2)
if TEST_DATE.weekday() in (5, 6):
    TEST_DATE += timedelta(days=7 - TEST_DATE.weekday())


@pytest.fixture(scope='session')
def amherst_customer_data() -> RowData:
    with PyCommence('Customer') as cmc:
        return cmc.read_row(pk='Test')


@pytest.fixture(scope='session')
def amherst_customer(amherst_customer_data) -> AmherstCustomer:
    return AmherstCustomer(row_id=amherst_customer_data.row_id, **amherst_customer_data.data)


# def test_auto_csv(amherst_customer):
#     ...
#     tracks = amherst_customer.tracking_links_in
#     print('\n RESULTS', tracks)
#     assert isinstance(tracks, list)
#     assert len(tracks) == 0


def test_it():
    cust = AmherstCustomer
    afield = cust.model_fields['name'].alias
    ...


# def test_sep():
#     pk = 'TEST RECORD DO NOT EDIT'
#     new_tracking_links = ['Link4', 'Link5', 'Link6']
#     new_tracking_numbers = ['Num4', 'Num5', 'Num6']
#     with pycommence_context('Hire') as pyc:
#         row = pyc.read_row(pk=pk)
#         record = AmherstHire(**row.data, row_info=row.row_info)
#         nums_field = record.alias_lookup('tracking_numbers')
#         tracking_numbers = record.tracking_numbers
#         tracking_numbers.extend(new_tracking_numbers)
#
#         links_field = record.alias_lookup('tracking_links_out')
#         old_links = record.tracking_links_out
#         old_links.extend(new_tracking_links)
#
#         update_package = {
#             links_field: CSV_SEPERATOR.join(old_links),
#             nums_field: CSV_SEPERATOR.join(tracking_numbers),
#         }
#
#         pyc.update_row(pk=pk, update_pkg=update_package)


def test_amherst_hire(amherst_customer_data: RowData):
    res = amherst_customer_data.construct_model()
    res = res.model_validate(res)
    assert res.name == 'TEST RECORD DO NOT EDIT'
