from __future__ import annotations

import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from amherst.models.hire_db_parts import HireState
from shipr import PFCom, express as el
from shipr.models import service_protocols as cp


class AmShipper(PFCom):

    def am_address_to_pf(self, address_am):
        town = self.get_town(address_am.postcode)
        addr_lines_dict = address_am.addr_lines_dict
        addr_lines_dict = {k: v for k, v in addr_lines_dict.items() if v.lower() != town.lower()}

        return el.types.AddressPF(
            **addr_lines_dict,
            town=town,
            postcode=address_am.postcode
        )

    def choose_hire_address(self, hire) -> el.types.AddressChoice:
        cmc_address = hire.hire_address.address
        candidates = self.get_candidates(hire.hire_address.postcode)
        add, score = super().choose_one_str(cmc_address, candidates)
        return el.types.AddressChoice(address=add, score=score)

    def choose_hire_address2(self, hire) -> el.types.AddressChoice:
        pf_address = self.am_address_to_pf(hire.hire_address)
        am_string = self.get_lines(pf_address)
        candidates = self.get_candidates(hire.hire_address.postcode)
        # cand_ls = [can.address_line1 + ' ' + can.address_line2 for can in candidates]
        add, score = super().choose_one_str(am_string, candidates)
        return el.types.AddressChoice(address=add, score=score)

    def get_lines(self, pf_address: el.types.AddressPF) -> str:
        lines = [pf_address.address_line1, pf_address.address_line2, pf_address.address_line3]
        ls = ' '.join(line for line in lines if line)

        return ls

    # def choose_hire_address1(self, hire) -> tuple[el.types.AddressPF, int]:
    #     candidates = self.get_candidates(hire.delivery_address.postcode)
    #     address_str = hire.delivery_address.address
    #     return super().choose_one_str(address_str, candidates)

    def hire_to_shipment_request(self, hire: HireWSubModels):
        ship_req = hire_to_shipment(hire)
        req = el.msg.CreateShipmentRequest(
            authentication=self.config.auth,
            requested_shipment=ship_req
        )
        return req

    def state_to_shipment_request(self, state: HireState):
        ship_req = state_to_shipment(state)
        req = el.msg.CreateShipmentRequest(
            authentication=self.config.auth,
            requested_shipment=ship_req
        )
        return req

    def get_shipment_resp(self, req: el.msg.CreateShipmentRequest) -> el.msg.CreateShipmentResponse:
        back = self.backend(cp.CreateShipmentService)
        resp = back.createshipment(request=req)
        return resp

    def state_to_response(self, state: HireState) -> el.msg.CreateShipmentResponse:
        req = self.state_to_shipment_request(state)
        return self.get_shipment_resp(req)


def hire_to_shipment(hire: HireWSubModels) -> el.shipment.RequestedShipmentMinimum:
    """Convert a Hire to a CreateShipmentRequest for the PFCom service."""
    req = el.shipment.RequestedShipmentMinimum(
        department_id=el.enums.DepartmentEnum.MAIN,
        shipment_type=el.enums.DeliveryTypeEnum.DELIVERY,
        contract_number=os.environ['PF_CONT_NUM_1'],
        service_code=el.enums.ServiceCode.EXPRESS24,
        shipping_date=hire.hire_dates.send_out_date,
        recipient_contact=amherst_hire_to_contact(hire),
        recipient_address=amherst_hire_to_address(hire),
        total_number_of_parcels=hire.hire_shipping.boxes,
    )
    return req


def amherst_hire_to_contact(hire: HireWSubModels) -> el.types.ContactPF:
    """Convert a Hire to a Contact for the PFCom service."""
    ret = el.types.ContactPF(**hire.contact_dict)
    return ret


def amherst_hire_to_address(hire: HireWSubModels) -> el.types.AddressPF:
    """Convert a Hire to an Address for the PFCom service."""
    ret = el.types.AddressPF(
        **hire.address_dict
    )
    return ret


def state_to_shipment(state: HireState) -> el.shipment.RequestedShipmentMinimum:
    req = el.shipment.RequestedShipmentMinimum(
        department_id=el.enums.DepartmentEnum.MAIN,
        shipment_type=el.enums.DeliveryTypeEnum.DELIVERY,
        contract_number=os.environ['PF_CONT_NUM_1'],
        service_code=el.enums.ServiceCode.EXPRESS24,
        shipping_date=state.ship_date,
        recipient_contact=state.recipient_contact,
        recipient_address=state.recipient_address,
        total_number_of_parcels=state.boxes,
    )
    return req
