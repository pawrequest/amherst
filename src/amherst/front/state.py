from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from amherst.models import HireDB
from amherst.shipping.pfcom import AmShipper

from shipr.models import pf_types as elt, pf_enums as ele
from shipr.models.pf_msg import CreateShipmentRequest, CreateShipmentResponse


class ShipState(elt.BasePFType):
    hire_id: int
    input_address: elt.AddressPF
    boxes: int = 1
    ship_date: Optional[date] = Field(default_factory=date.today)
    ship_service: Optional[ele.ServiceCode] = ele.ServiceCode.EXPRESS24
    candidates: list[elt.AddressPF] = Field(default_factory=list)
    contact: Optional[elt.ContactPF] = Field(default=None)
    address_choice: Optional[elt.AddressChoice] = Field(default=None)
    request: Optional[CreateShipmentRequest] = Field(default=None)
    response: Optional[CreateShipmentResponse] = Field(default=None)

    @property
    def export(self):
        return self.model_dump_json(exclude={'candidates'})

    def update(self, **kwargs):
        return self.model_copy(update=kwargs)

    @field_validator('ship_date', mode='after')
    def validate_ship_date(cls, v):
        tod = date.today()
        return v if v >= tod else tod



def state_from_hire(hire: HireDB, pfcom: AmShipper) -> ShipState:
    state = ShipState(hire_id=hire.id, input_address=hire.address)
    state.boxes = hire.boxes
    state.ship_date = hire.ship_date
    state.contact = hire.contact
    state.candidates = pfcom.get_candidates(hire.address.postcode)
    state.address_choice = pfcom.guess_address(hire.address)
    return ShipState.model_validate(state)
