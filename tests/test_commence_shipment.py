import os

from pycommence import pycommence_context
from shipaw.fapi.responses import ShipmentResponse
from shipaw.utils.consts_enums import ShipDirection

from amherst.models.amherst_models import AmherstCustomer
from amherst.models.commence_shipment import CommenceShipment
from amherst.models.shipment import AmherstShipment


def test_create():
    ship = CommenceShipment(
        direction=ShipDirection.OUTBOUND,
        customer=['Test'],
        label=r'C:\prdev\data\sandbox\labels\Outbound\Shipping_Label_TO_Test_Company_ON_2026-04-03.pdf',
    )
    shpdict = ship.model_dump(by_alias=True)
    with pycommence_context(csrname='Shipment') as cmc:
        res = cmc.create_row(shpdict, csrname='Shipment')

    ...


def test_1():
    with pycommence_context(csrname='Customer') as cmc:
        res = cmc.read_row(pk='Test')
        obj = AmherstCustomer(row_info=res.row_info, **res.data)
        ...
