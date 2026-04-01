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
        customers=['Test'],
        label=r'C:\prdev\data\sandbox\labels\Outbound\Shipping_Label_TO_Test_Company_ON_2026-04-03.pdf',
    )
    shpdict = ship.model_dump(by_alias=True)
    with pycommence_context(csrname='Shipment') as cmc:
        res = cmc.create_row(shpdict, csrname='Shipment')

    ...


def test_1():
    with pycommence_context(csrname='Shipment') as cmc:
        res = cmc.read_row(pk='2026-April-1st (Wednesday @ 20:42:02)')
        obj = CommenceShipment(**res.data)
    ...
