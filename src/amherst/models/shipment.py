from functools import cached_property
from typing import TYPE_CHECKING

from pycommence.meta.meta import get_table_type
from pydantic import Field, field_validator

# if TYPE_CHECKING:
from amherst.models.amherst_models import AmherstShipableBase
from shipaw.fapi.requests import ShipmentRequest
from shipaw.models.shipment import Shipment


class AmherstShipment(Shipment):
    context: dict = Field(default_factory=dict)
    record_: AmherstShipableBase = Field(None, init=False)

    @field_validator('context', mode='after')
    def val_context(cls, v):
        try:
            row_id = v['row_id']
        except KeyError as e:
            raise ValueError(f'Missing row_id in context record: {v.get("record")}') from e
        return v

    @cached_property
    def record(self) -> 'AmherstShipableBase':
        if self.record_ is None:
            category = self.context.get('category')
            model_type = get_table_type(category)
            self.record_ = model_type.model_validate(self.context)
        return self.record_


class AmherstShipmentRequest(ShipmentRequest):
    shipment: AmherstShipment
