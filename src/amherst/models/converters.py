from amherst.models.amherst_models import AmherstTableBase
from shipaw.models.pf_shipment_configured import ShipmentConfigured, to_collection, to_dropoff
from shipaw.ship_types import ShipDirection


def to_shipment(amtable: AmherstTableBase, direction: ShipDirection):
    ship = ShipmentConfigured.model_validate(amtable.shipment_dict())
    match direction:
        case ShipDirection.Outbound:
            return ship
        case ShipDirection.Inbound:
            return to_collection(ship)
        case ShipDirection.Dropoff:
            return to_dropoff(ship)
        case _:
            raise ValueError(f'Unknown direction {direction}')
