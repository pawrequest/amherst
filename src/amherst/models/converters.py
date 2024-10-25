from amherst.models.amherst_models import AmherstTableBase
from shipaw.models.pf_shipment import to_collection, to_dropoff, Shipment
from shipaw.ship_types import ShipDirection


def to_shipment(amtable: AmherstTableBase, direction: ShipDirection):
    ship = Shipment.model_validate(amtable.shipment_dict())
    match direction:
        case ShipDirection.OUTBOUND:
            return ship
        case ShipDirection.INBOUND:
            return to_collection(ship)
        case ShipDirection.DROPOFF:
            return to_dropoff(ship)
        case _:
            raise ValueError(f'Unknown direction {direction}')
