import pytest

from amherst.models.am_record_smpl import AmherstTable, get_am_record, AmherstGenericIn
from shipaw.models.pf_shipment import Shipment
from .fixtures_mock import customer_record_xmpl, hire_record_xmpl, sale_record_xmpl


@pytest.fixture(params=[('Hire', hire_record_xmpl), ('Sale', sale_record_xmpl), ('Customer', customer_record_xmpl)])
def amrec(request) -> AmherstTable:
    table, record = request.param
    record['category'] = table
    record = get_am_record(record)
    return record


def test_get_amrec(amrec: AmherstTable):
    assert isinstance(amrec, AmherstTable)
    assert isinstance(amrec.customer_record, AmherstTable)
    gen = AmherstGenericIn.model_validate(amrec, from_attributes=True)
    assert isinstance(gen, AmherstGenericIn)


def test_get_shiprec(amrec: AmherstTable):
    ship = amrec.shipment_dict
    shipment = Shipment.model_validate(ship)
    assert isinstance(shipment, Shipment)
