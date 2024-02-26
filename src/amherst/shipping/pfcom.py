from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amherst.front.state import ShipState

from shipr import PFCom, express as el, types as elt


class AmShipper(PFCom):

    def state_to_shipment_request(self, state: ShipState):
        ship_req = state_to_shipment(state)
        req = el.msg.CreateShipmentRequest(
            authentication=self.config.auth,
            requested_shipment=ship_req
        )
        return req

    def state_to_response(self, state: ShipState) -> el.msg.CreateShipmentResponse:
        req = self.state_to_shipment_request(state)
        return self.get_shipment_resp(req)


def state_to_shipment(state: ShipState) -> el.shipment.RequestedShipmentMinimum:
    add = elt.AddressPF.model_validate(state.address_choice.address)
    req = el.shipment.RequestedShipmentMinimum(
        department_id=el.enums.DepartmentEnum.MAIN,
        shipment_type=el.enums.DeliveryTypeEnum.DELIVERY,
        contract_number=os.environ['PF_CONT_NUM_1'],
        service_code=el.enums.ServiceCode.EXPRESS24,
        shipping_date=state.ship_date,
        recipient_contact=state.contact,
        recipient_address=add,
        total_number_of_parcels=state.boxes,
    )
    return req
