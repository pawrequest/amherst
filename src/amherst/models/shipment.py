from functools import cached_property
from typing import TYPE_CHECKING

from pydantic import Field, field_validator

if TYPE_CHECKING:
    from amherst.models.amherst_models import AmherstShipableBase
from amherst.models.commence_adaptors import AmherstRowInfo
from amherst.models.meta import get_table_model
from shipaw.fapi.requests import ShipmentRequest
from shipaw.models.shipment import Shipment


class AmherstShipment(Shipment):
    context: dict = Field(default_factory=dict)

    @field_validator('context', mode='after')
    def val_context(cls, v):
        if 'record' not in v:
            raise ValueError('context must include a "record" key')
        if not hasattr(v['record'], 'row_info') and 'row_info' not in v['record']:
            raise ValueError('context["record"] must include a "row_info" key')
        return v

    @cached_property
    def row_info(self) -> AmherstRowInfo:
        res = self.record_dict.get('row_info')
        return AmherstRowInfo(category=res[0], id=res[1])

    @cached_property
    def record_dict(self):
        return self.context.get('record')

    @cached_property
    def record(self) -> 'AmherstShipableBase':
        model_type = get_table_model(self.row_info.category)
        return model_type.model_validate(self.record_dict)


class AmherstShipmentRequest(ShipmentRequest):
    shipment: AmherstShipment
