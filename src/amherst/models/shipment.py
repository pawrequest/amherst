from pydantic import Field
from unicodedata import category

from amherst.models.commence_adaptors import AmherstRowInfo
from amherst.models.meta import get_table_model
from shipaw.fapi.requests import ShipmentRequest
from shipaw.models.shipment import Shipment


class AmherstShipment(Shipment):
    context: dict = Field(default_factory=dict)

    @property
    def row_info(self) -> AmherstRowInfo:
        res = self.context.get('record').get('row_info')
        return AmherstRowInfo(category=res[0], id=res[1])

    @property
    def record_dict(self):
        return self.context.get('record')

    @property
    def record(self):
        model_type = get_table_model(self.row_info.category)
        return model_type.model_validate(self.record_dict)


class AmherstShipmentrequest(ShipmentRequest):
    shipment: AmherstShipment
