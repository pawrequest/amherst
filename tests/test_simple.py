import random
from pprint import pprint

import pytest
import pytest_asyncio
from loguru import logger

from amherst.commence_adaptors import initial_filter
from amherst.models.am_record_smpl import AmherstTableBase, amrec_booking, get_amrec_db_smpl, AmherstTableDB
from pycommence.pycommence_v2 import PyCommence
from shipaw.models.pf_shipment import Shipment


@pytest.fixture(
    params=['Hire', 'Sale', 'Customer'],
)
def pycmc(request) -> PyCommence:
    table = request.param
    cmc = PyCommence.with_csr(table, filter_array=initial_filter(table))
    logger.info(f'testing against {cmc.get_csr().row_count} {table} records')
    yield cmc


@pytest_asyncio.fixture
async def amrec(pycmc: PyCommence):
    record = random.choice(list(pycmc.generate_records_ids()))
    logger.info(f'testing {record["Name"]}')
    record['category'] = pycmc.get_csr().category
    pprint(record)
    amrec = get_amrec_db_smpl(record)
    return amrec


# @pytest.fixture(params=[('Hire', hire_record_xmpl), ('Sale', sale_record_xmpl), ('Customer', customer_record_xmpl)])
# def amrec(request) -> AmherstTable:
#     table, record = request.param
#     record['category'] = table
#     record = get_am_record_smpl(record)
#     record = AmherstTable.model_validate(record, from_attributes=True)
#     return record


def test_get_amrec(amrec: AmherstTableBase):
    assert isinstance(amrec, AmherstTableBase)


def test_get_shiprec(amrec: AmherstTableBase):
    ship = amrec.shipment_dict
    shipment = Shipment.model_validate(ship)
    assert isinstance(shipment, Shipment)


def test_add_simple(test_session_fxt, amrec):
    amrecdb = AmherstTableDB.model_validate(amrec, from_attributes=True)
    test_session_fxt.add(amrecdb)
    test_session_fxt.commit()
    test_session_fxt.refresh(amrecdb)
    assert amrec.row_id


def test_():
    pass