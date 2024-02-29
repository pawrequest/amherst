import shipr.models.extended
from shipr.models.el_msg import FindRequest, FindResponse
from shipr.models import service_protocols as cp


def test_pfc2(pfcom):
    back = pfcom.backend(cp.FindService)
    auth = pfcom.config.auth
    req = FindRequest(authentication=auth, paf=shipr.models.exp.PAF(postcode="NW6 4TE"))
    response = back.find(request=req)
    assert isinstance(response, FindResponse)
    assert isinstance(response.paf, shipr.models.exp.PAF)
    assert isinstance(response.paf.specified_neighbour[0].address[0], shipr.models.exp.AddressRecipient)


def test_choose_address(pfcom, random_hire_db):
    choice = pfcom.choose_address(random_hire_db.address)
    assert isinstance(choice.address_dict, shipr.models.exp.AddressRecipient)
