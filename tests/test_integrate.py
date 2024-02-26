import datetime
import os

from thefuzz import fuzz, process

from amherst.models import HireWSubModels
from amherst.shipping.pfcom import AmShipper
from shipr.express.types import AddressPF, PAF
from shipr.models.service_protocols import CreateShipmentService, FindService, PrintLabelService
from shipr.express.msg import (
    CreateShipmentRequest,
    FindRequest,
    FindResponse, PrintLabelRequest, PrintLabelResponse,
)
from shipr.express.shipment import RequestedShipmentMinimum


def test_pfc2(zconfig, pfcom):
    back = pfcom.backend(FindService)
    req = FindRequest(authentication=zconfig.auth, paf=PAF(postcode='NW6 4TE'))
    response = back.find(request=req)
    assert isinstance(response, FindResponse)
    assert isinstance(response.paf, PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], AddressPF)


def hire_to_shipment_request(hire: HireWSubModels, pfcom: AmShipper):
    ship_req = pfcom.hire_to_shipment_request(hire)
    back = pfcom.backend(CreateShipmentService)
    req = CreateShipmentRequest(authentication=pfcom.config.auth, requested_shipment=ship_req)
    resp = back.createshipment(request=req)
    return resp


def test_hire_to_shipment(pfcom, hire_in):
    req = pfcom.hire_to_shipment_request(hire_in)
    resp = pfcom.get_shipment_resp(req)
    shipment_ = resp.completed_shipment_info.completed_shipments.completed_shipment[0]
    ship_num = shipment_.shipment_number
    assert isinstance(ship_num, str)
    pfcom.get_label(ship_num)


def get_label(pf_com2, pf_auth, ship_num):
    back = pf_com2.backend(PrintLabelService)
    req = PrintLabelRequest(authentication=pf_auth, shipment_number=ship_num)
    response: PrintLabelResponse = back.printlabel(request=req)
    outpath = response.label.download()
    os.startfile(outpath)


def get_postocde_addresses(postcode: str, pf_com2, zconfig):
    back = pf_com2.backend(FindService)
    req = FindRequest(authentication=zconfig.auth, paf=PAF(postcode=postcode))
    response = back.find(request=req)
    addresses = [
        neighbour.address[0]
        for neighbour in response.paf.specified_neighbour
    ]
    return addresses


def choose_address(address_str: str, candidates: list):
    res = process.extractOne(address_str, candidates, scorer=fuzz.token_sort_ratio)
    return res


def test_check_address(pfcom, zconfig, hire_in):
    candidates = get_postocde_addresses(hire_in.hire_address.postcode, pfcom, zconfig)
    address = hire_in.hire_address
    res = choose_address(address.address, candidates)
    ...


def shipment_from_address_contact(address, contact):
    ship_date = datetime.date.today() + datetime.timedelta(days=1)
    if not ship_date.isoweekday() > 5:
        ship_date = ship_date + datetime.timedelta(days=2)

    return RequestedShipmentMinimum.from_minimal(
        ship_date=ship_date,
        contact=contact,
        address=address,
        num_parcels=1
    )
