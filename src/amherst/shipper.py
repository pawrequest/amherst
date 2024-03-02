# from __future__ import annotations

import os

import shipr.models.pf_ext
import shipr.models.pf_shared
import shipr.models.pf_top
from shipr.models.ui_states.states import ShipState
from shipr.models import pf_msg, pf_shared, pf_top
from shipr import ELClient


class AmShipper(ELClient):
    def state_to_shipment_request(self, state: ShipState):
        ship_req = booking_state_to_shipment(state)
        req = pf_msg.CreateShipmentRequest(authentication=self.config.auth, requested_shipment=ship_req)
        return req

    def state_to_response(self, state: ShipState) -> pf_msg.CreateShipmentResponse:
        req = self.state_to_shipment_request(state)
        return self.get_shipment_resp(req)


def booking_state_to_shipment(state: ShipState) -> pf_top.RequestedShipmentMinimum:
    # add = elt.AddressRecipientPF.model_validate(state.address)
    return pf_top.RequestedShipmentMinimum(
        department_id=pf_shared.DepartmentNum,
        shipment_type='DELIVERY',
        contract_number=os.environ["PF_CONT_NUM_1"],
        service_code=state.ship_service,
        shipping_date=state.ship_date,
        recipient_contact=state.contact,
        recipient_address=state.address,
        total_number_of_parcels=state.boxes,
    )
