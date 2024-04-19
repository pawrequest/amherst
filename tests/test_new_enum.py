import pycommence
import pytest

from amherst.models.shipable_item import ShipableRecord

type OrDict[T] = T | dict[str, T]

home_data = {
    'Customer': 'Test',
    'Hire': 'Test Customer - 2/21/2024 ref 43383',
    'Sale': 'Test - 22/10/2022 ref 1',
}


@pytest.mark.parametrize("key, name", home_data.items())
def test_smth(key, name):
    py_com = pycommence.PyCommence.from_table_name(key)
    record = py_com.one_record(name)
    record['cmc_table_name'] = key
    val = ShipableRecord.model_validate(record)
    ...


