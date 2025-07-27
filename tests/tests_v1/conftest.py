import pytest

from shipaw.expresslink_client import ELClient
from shipaw.pf_config import PFSandboxSettings, pf_sandbox_sett


@pytest.fixture(scope='session')
def sett():
    settings = pf_sandbox_sett()
    PFSandboxSettings.model_validate(settings, from_attributes=True)
    yield settings


@pytest.fixture(scope='session')
def el_client(sett):
    yield ELClient(settings=sett)

# @pytest.mark.usefixtures('booking_mock', 'random_booking')
# @pytest_asyncio.fixture(
#     params=['booking_mock', 'random_booking'],
# )
# async def booking_fxt(request):
#     print(f'request.param: {request.param}')
#     booking = request.getfixturevalue(request.param)
#     yield booking


# __all__ = [
#     'test_session_fxt',
#     'sett',
#     'el_client',
#     'random_booking',
#     'random_booking',
#     'random_booking_in_db',
#     'random_booking',
#     'random_amrec',
#     'pycmc',
#     'contact_xmpl',
#     'address_xmpl',
#     'booking_mock_fxt',
#     'booking_mock_db',
#     'amrec_mock',
# ]
