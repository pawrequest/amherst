# from __future__ import annotations

import os

import shipr.models.extended
import shipr.models.shipr_shared
from amherst.models.hire_state import HireState
from shipr.models import el_enums


from shipr import ELClient, el_ship, el_msg


class AmShipper(ELClient):
    def state_to_shipment_request(self, state: HireState):
        ship_req = booking_state_to_shipment(state)
        req = el_msg.CreateShipmentRequest(authentication=self.config.auth, requested_shipment=ship_req)
        return req

    def state_to_response(self, state: HireState) -> el_msg.CreateShipmentResponse:
        req = self.state_to_shipment_request(state)
        return self.get_shipment_resp(req)


def booking_state_to_shipment(state: HireState) -> shipr.models.extended.RequestedShipmentMinimum:
    # add = elt.AddressRecipientPF.model_validate(state.address)
    return shipr.models.extended.RequestedShipmentMinimum(
        department_id=shipr.models.shared.DepartmentNum.MAIN,
        shipment_type=shipr.models.shared.DeliveryKind.DELIVERY,
        contract_number=os.environ["PF_CONT_NUM_1"],
        service_code=state.ship_service,
        shipping_date=state.ship_date,
        recipient_contact=state.contact,
        recipient_address=state.address,
        total_number_of_parcels=state.boxes,
    )
