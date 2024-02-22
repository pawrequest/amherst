import os
from pathlib import Path

from thefuzz import fuzz, process

from shipr.models.express.expresslink_types import PAF
from ..models import Hire
from ..converters import amherst_hire_to_pfc_shipment
from shipr import (
    AddressPF,
    CreateShipmentRequest,
    CreateShipmentService,
    FindRequest,
    FindService,
    PFCom,
    PrintLabelRequest,
    PrintLabelResponse,
    PrintLabelService,
)


def hire_to_shipment_request(hire: Hire, pf_com2: PFCom):
    """Convert a Hire to a CreateShipmentRequest for the PFCom service.

    args:
        hire: Hire
        pf_com2: PFCom - PFCom combadge client
    """
    ship_req = amherst_hire_to_pfc_shipment(hire)
    req = CreateShipmentRequest(authentication=pf_com2.config.auth, requested_shipment=ship_req)
    back = pf_com2.backend(CreateShipmentService)
    resp = back.createshipment(request=req)
    return resp


def get_label(pf_com: PFCom, ship_num) -> Path:
    """Get the label for a shipment number.

    args:
        pf_com2: PFCom - PFCom combadge client
        pf_auth: Authentication - PFCom authentication
        ship_num: str - shipment number
    """
    back = pf_com.backend(PrintLabelService)
    req = PrintLabelRequest(authentication=pf_com.config.auth, shipment_number=ship_num)
    response: PrintLabelResponse = back.printlabel(request=req)
    outpath = response.label.download()
    os.startfile(outpath)
    return outpath


def get_postocde_addresses(postcode: str, pf_com) -> list[AddressPF]:
    back = pf_com.backend(FindService)
    req = FindRequest(authentication=pf_com.config.auth, paf=PAF(postcode=postcode))
    response = back.find(request=req)
    addresses = [
        neighbour.address[0]
        for neighbour in response.paf.specified_neighbour
    ]
    return addresses


def choose_one(address_str: str, candidates: list) -> tuple[AddressPF, int]:
    res = process.extractOne(address_str, candidates, scorer=fuzz.token_sort_ratio)
    return res


def choose_hire_address(hire, pf_com) -> tuple[AddressPF, int]:
    candidates = get_postocde_addresses(hire.delivery_address.postcode, pf_com)
    address = hire.delivery_address
    chosen_add, score = choose_one(address.address, candidates)
    return chosen_add, score
