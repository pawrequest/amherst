import pytest

from shipr.models import pf_ext, pf_top


# @pytest.mark.skip(reason="many api calls")
# def test_address_and_contact(
#         random_hires: list[hire_model.Hire],
#         pfcom,
#         test_session
# ):
#     for hire in random_hires:
#         address = pfcom.choose_address(hire.input_address)
#         address = pf_ext.AddressRecipient.model_validate(address)
#         contact = pf_top.Contact.model_validate(hire.contact)
#         assert address is not None and contact is not None
