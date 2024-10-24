import pytest


#
#
# def test_uk_pc_utils():
#     from ukpostcodeutils import validation
#
#     assert validation.is_valid_postcode('me8 8sp'.replace(' ', '').upper())


#
#
@pytest.mark.parametrize('postcode', ['NW6 4TE', 'ME8 8SP'])
def test_el_pc(el_client, postcode):
    fixed = postcode.upper().strip().replace('  ', ' ')
    candidates = el_client.get_candidates(fixed)
    assert candidates[0].address_line1
