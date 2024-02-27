
from shipr.models.pf_msg import FindRequest, FindResponse
from shipr.models import pf_types as elt, service_protocols as cp


def test_pfc2(pfcom):
    back = pfcom.backend(cp.FindService)
    auth = pfcom.config.auth
    req = FindRequest(authentication=auth, paf=elt.PAF(postcode='NW6 4TE'))
    response = back.find(request=req)
    assert isinstance(response, FindResponse)
    assert isinstance(response.paf, elt.PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], elt.AddressPF)


def test_choose_address(pfcom, random_hire_db):
    choice = pfcom.address_choice_addr(random_hire_db.address)
    assert isinstance(choice.address, elt.AddressPF)
