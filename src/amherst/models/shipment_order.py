from pydantic import BaseModel
from shipaw.models.shipment import Shipment

from amherst.models.amherst_models import AmherstShipableBase


class ShipmentOrder[T:AmherstShipableBase](BaseModel):
    shipment: Shipment
    record: T
