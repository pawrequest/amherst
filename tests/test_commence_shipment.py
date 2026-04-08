from amherst_core.models import CommenceShipment
from pycommence import PyCommence
from shipaw.utils.consts_enums import ShipDirection


def test_create():
    ship = CommenceShipment(
        direction=ShipDirection.OUTBOUND,
        customers=['Test'],
        label=r'C:\prdev\data\sandbox\labels\Outbound\Shipping_Label_TO_Test_Company_ON_2026-04-03.pdf',
    )
    shpdict = ship.model_dump(by_alias=True)
    with PyCommence('Shipment') as cmc:
        res = cmc.cursor().create_row(shpdict)

    ...


def test_1():
    with PyCommence('Shipment') as cmc:
        res = cmc.read_row(pk='2026-April-1st (Wednesday @ 20:42:02)')
        obj = CommenceShipment(**res.data)
    ...
