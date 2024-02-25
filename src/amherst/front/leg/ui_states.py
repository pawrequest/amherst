from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from combadge.core.interfaces import SupportsService
from pydantic import BaseModel, Field, model_validator, field_validator

from amherst.models import Hire
from amherst.shipping.pfcom import AmShipper
from shipr.express import types as elt
from shipr.express.shared import BaseRequest


class UIState(BaseModel):
    pass


class HireUIState(UIState):
    pfcom: AmShipper
    hire: Hire
    boxes: int = Field(1)
    ship_date: Optional[date] = Field(None)
    candidates: list[elt.AddressPF] = Field(default_factory=list)
    chosen_address: Optional[elt.AddressChoice] = None

    def get_addresses(self):
        self.candidates = self.pfcom.get_candidates(self.hire.delivery_address.postcode)
        self.chosen_address = self.pfcom.choose_hire_address(self.hire)

    @model_validator(mode='after')
    def validate_mod(self):
        tod = datetime.today().date()
        sd = self.ship_date or self.hire.dates.send_out_date
        self.ship_date = sd if sd >= tod else tod
        self.boxes = self.boxes or self.hire.shipping.boxes
        self.get_addresses()
        return self

#