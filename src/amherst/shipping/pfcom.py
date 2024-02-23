import os

from amherst.models import Hire
from shipr import PFCom, types as elt
from shipr.models import combadge_protocols as cp
from shipr import express as el


class AmShipper(PFCom):
    def choose_hire_address(self, hire) -> elt.AddressChoice:
        candidates = self.get_candidates(hire.delivery_address.postcode)
        address_str = hire.delivery_address.address
        add, score = super().choose_one_str(address_str, candidates)
        return elt.AddressChoice(address=add, score=score)

    def hire_to_shipment_request(self, hire: Hire):
        """Convert a Hire to a CreateShipmentRequest for the PFCom service.

        args:
            hire: Hire
            pf_com2: PFCom - PFCom combadge client
        """
        ship_req = hire_to_shipment(hire)
        req = el.msg.CreateShipmentRequest(
            authentication=self.config.auth,
            requested_shipment=ship_req
        )
        return req

    def get_shipment_resp(self, req: el.msg.CreateShipmentRequest) -> el.msg.CreateShipmentResponse:
        back = self.backend(cp.CreateShipmentService)
        resp = back.createshipment(request=req)
        return resp


def hire_to_shipment(hire: Hire) -> el.shipment.RequestedShipmentMinimum:
    """Convert a Hire to a CreateShipmentRequest for the PFCom service."""
    req = el.shipment.RequestedShipmentMinimum(
        department_id=el.enums.DepartmentEnum.MAIN,
        shipment_type=el.enums.DeliveryTypeEnum.DELIVERY,
        contract_number=os.environ['PF_CONT_NUM_1'],
        service_code=el.enums.ServiceCode.EXPRESS24,
        shipping_date=hire.dates.send_out_date,
        recipient_contact=amherst_hire_to_contact(hire),
        recipient_address=amherst_hire_to_address(hire),
        total_number_of_parcels=hire.shipping.boxes,
    )
    return req


def amherst_hire_to_contact(hire: Hire) -> el.types.ContactPF:
    """Convert a Hire to a Contact for the PFCom service."""
    ret = el.types.ContactPF(**hire.contact_dict)
    return ret


def amherst_hire_to_address(hire: Hire) -> el.types.AddressPF:
    """Convert a Hire to an Address for the PFCom service."""
    ret = el.types.AddressPF(
        **hire.address_dict
    )
    return ret
