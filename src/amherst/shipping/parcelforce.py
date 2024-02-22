import os
from pathlib import Path

from thefuzz import fuzz, process

from shipr import PFCom
from shipr.models import express as el, combadge_protocols as cp
from ..models import Hire
from ..converters import amherst_hire_to_pfc_shipment


def hire_to_shipment_request(hire: Hire, pf_com2: PFCom):
    """Convert a Hire to a CreateShipmentRequest for the PFCom service.

    args:
        hire: Hire
        pf_com2: PFCom - PFCom combadge client
    """
    ship_req = amherst_hire_to_pfc_shipment(hire)
    req = el.msg.CreateShipmentRequest(authentication=pf_com2.config.auth, requested_shipment=ship_req)
    back = pf_com2.backend(cp.CreateShipmentService)
    resp = back.createshipment(request=req)
    return resp


def get_label(pf_com: PFCom, ship_num) -> Path:
    """Get the label for a shipment number.

    args:
        pf_com2: PFCom - PFCom combadge client
        pf_auth: Authentication - PFCom authentication
        ship_num: str - shipment number
    """
    back = pf_com.backend(cp.PrintLabelService)
    req = el.msg.PrintLabelRequest(authentication=pf_com.config.auth, shipment_number=ship_num)
    response: el.msg.PrintLabelResponse = back.printlabel(request=req)
    outpath = response.label.download()
    os.startfile(outpath)
    return outpath


def get_postocde_addresses(postcode: str, pf_com) -> list[el.types.AddressPF]:
    back = pf_com.backend(cp.FindService)
    req = el.msg.FindRequest(authentication=pf_com.config.auth, paf=el.types.PAF(postcode=postcode))
    response = back.find(request=req)
    if not response.paf.specified_neighbour:
        return []
    addresses = [
        neighbour.address[0]
        for neighbour in response.paf.specified_neighbour
    ]
    return addresses


def choose_one(address_str: str, candidates: list) -> tuple[el.types.AddressPF, int]:
    res = process.extractOne(address_str, candidates, scorer=fuzz.token_sort_ratio)
    return res


def choose_hire_address(hire, candidates) -> tuple[el.types.AddressPF, int]:
    address = hire.delivery_address
    chosen_add, score = choose_one(address.address, candidates)
    return chosen_add, score
