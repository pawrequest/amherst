from pathlib import Path

from shipr.express.msg import (
    FindRequest,
    FindResponse,
)
from shipr.models import service_protocols as cp
from shipr.express import types as elt


def test_pfc2(pfcom):
    back = pfcom.backend(cp.FindService)
    auth = pfcom.config.auth
    req = FindRequest(authentication=auth, paf=elt.PAF(postcode='NW6 4TE'))
    response = back.find(request=req)
    assert isinstance(response, FindResponse)
    assert isinstance(response.paf, elt.PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], elt.AddressPF)


def test_hire_to_shipment(pfcom, hire_in):
    req = pfcom.hire_to_shipment_request(hire_in)
    resp = pfcom.get_shipment_resp(req)
    shipment_ = resp.completed_shipment_info.completed_shipments.completed_shipment[0]
    ship_num = shipment_.shipment_number
    assert isinstance(ship_num, str)
    res = pfcom.get_label(ship_num)
    assert isinstance(res, Path)


def test_choose_address(pfcom, hire_in):
    add, score = pfcom.choose_hire_address(hire_in)
    assert isinstance(add, elt.AddressPF)



