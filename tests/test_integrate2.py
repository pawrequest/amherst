from pathlib import Path

from amherst.shipping.parcelforce import (
    hire_to_shipment_request,
    get_label,
    get_postocde_addresses,
    choose_one,
)
from shipr.models.combadge_protocols import FindService
from shipr import AddressPF
from shipr.models.express.expresslink_pydantic import PAF, Authentication
from shipr.models.express.msg import (
    FindRequest,
    FindResponse,
)


def test_pfc2(pf_com):
    back = pf_com.backend(FindService)
    auth = pf_com.config.auth
    req = FindRequest(authentication=auth, paf=PAF(postcode='NW6 4TE'))
    response = back.find(request=req)
    assert isinstance(response, FindResponse)
    assert isinstance(response.paf, PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], AddressPF)


def test_hire_to_shipment(pf_auth, pf_com, hire_fxt):
    resp = hire_to_shipment_request(hire_fxt, pf_com)
    shipment_ = resp.completed_shipment_info.completed_shipments.completed_shipment[0]
    ship_num = shipment_.shipment_number
    assert isinstance(ship_num, str)
    res = get_label(pf_com, pf_auth, ship_num)
    assert isinstance(res, Path)


def test_choose_address(pf_com, zconfig, hire_fxt):
    candidates = get_postocde_addresses(hire_fxt.delivery_address.postcode, pf_com)
    address = hire_fxt.delivery_address
    add, score = choose_one(address.address, candidates)
    assert isinstance(add, AddressPF)



