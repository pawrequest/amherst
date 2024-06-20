import pytest
from fastapi.encoders import jsonable_encoder

from amherst.models.db_models import BookingStateDB
from shipaw.models.booking_states import BookingState
from shipaw.models.pf_msg import ShipmentResponse


@pytest.mark.asyncio
async def test_ping(test_client):
    response = test_client.get('/api/ping')
    assert response.status_code == 200
    assert response.json() == {'ping': 'pong'}


@pytest.mark.asyncio
async def test_candidates(test_client):
    response = test_client.get('/api/candidates', params={'postcode': 'NW1 1AA'})
    assert response.status_code == 200
    print(response.json())
    # assert response.json() == {'candidates': 'candidates'}


@pytest.mark.asyncio
async def test_retrieve_random_booking(test_client, random_booking_in_db):
    response = test_client.get(f'/api/{random_booking_in_db.id}')
    resp_json = response.json()
    booking = BookingState.model_validate(resp_json)

    assert isinstance(booking, BookingState)
    assert response.status_code == 200
    assert resp_json['id'] == random_booking_in_db.id


@pytest.mark.asyncio
async def test_shiprec(test_client, random_booking_in_db):
    ...


@pytest.mark.asyncio
async def test_confirm_booking(test_client, random_booking_in_db: BookingStateDB):
    shipment_request_dict = jsonable_encoder(random_booking_in_db.shipment_request)
    response = test_client.post('/api/confirm_booking', json=shipment_request_dict)
    resp_json = response.json()
    ship_resp = ShipmentResponse.model_validate(resp_json)

    assert response.status_code == 200
    assert isinstance(ship_resp, ShipmentResponse)
