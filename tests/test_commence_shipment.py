import os

from pycommence import pycommence_context
from shipaw.fapi.responses import ShipmentResponse
from shipaw.models.ship_types import ShipDirection

from amherst.models.commence_shipment import CommenceShipment
from amherst.models.shipment import AmherstShipment


def test_create():
    ship = CommenceShipment(
        direction=ShipDirection.OUTBOUND,
        customer=['Test']
    )
    shpdict = ship.model_dump(by_alias=True)
    with pycommence_context(csrname='Shipment') as cmc:
        res = cmc.create_row(shpdict, csrname='Shipment')

    ...


def shipment_obj(shipment: AmherstShipment, shipment_response: ShipmentResponse) -> CommenceShipment:
    record = shipment.record
    res = CommenceShipment(
        direction=shipment.direction,
        customer=[record.customer_name],
        tracking_links=shipment_response.tracking_links,
        latest_tracking=shipment_response.tracking_links[0] if shipment_response.tracking_links else None,
    )
    setattr(res, record.category.lower(), record.name)
    return res
