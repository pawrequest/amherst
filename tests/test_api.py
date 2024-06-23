import pytest
from fastapi.encoders import jsonable_encoder
from starlette.testclient import TestClient

from amherst.models.db_models import BookingStateDB
from .client import test_client  # noqa: F401
from .fixtures_live import random_booking_in_db  # noqa: F401
from .fixtures_mock import booking_mock_db, booking_mock_fxt, amrec_mock  # noqa: F401
from shipaw.models.booking_states import BookingState
from shipaw.models.pf_msg import ShipmentResponse

b_fxt = booking_mock_db


# b_fxt = random_booking_in_db

@pytest.mark.asyncio
async def test_ping(test_client: TestClient):
    response = test_client.get('/api/ping')
    assert response.status_code == 200
    assert response.json() == {'ping': 'pong'}


@pytest.mark.asyncio
async def test_candidates(test_client):
    response = test_client.get('/api/candidates', params={'postcode': 'NW1 1AA'})
    assert response.status_code == 200
    print(response.json())
    # assert response.json() == {'candidates': 'candidates'}


# noinspection PyShadowingNames
@pytest.mark.asyncio
async def test_retrieve_random_booking(test_client, b_fxt: BookingStateDB):
    response = test_client.get(f'/api/{b_fxt.id}')
    resp_json = response.json()
    booking = BookingState.model_validate(resp_json)

    assert isinstance(booking, BookingState)
    assert response.status_code == 200
    assert resp_json['id'] == b_fxt.id


# noinspection PyShadowingNames
@pytest.mark.asyncio
async def test_confirm_booking(test_client, b_fxt):
    shipment_request_dict = jsonable_encoder(b_fxt.shipment_request)
    response = test_client.post('/api/confirm_booking', json=shipment_request_dict)
    resp_json = response.json()
    ship_resp = ShipmentResponse.model_validate(resp_json)

    assert response.status_code == 200
    assert isinstance(ship_resp, ShipmentResponse)
