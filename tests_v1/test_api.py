import pytest
from fastapi.encoders import jsonable_encoder
from starlette.testclient import TestClient

from shipaw.models.pf_msg import ShipmentResponse
from shipaw.models.pf_shipment_configured import ShipmentAwayCollectionConfigured
from client import test_client  # noqa: F401
from .fixtures_live import random_booking_in_db  # noqa: F401
from .fixtures_mock import FAKE_EMAIL, FAKE_PHONE, amrec_mock, booking_mock_db, booking_mock_fxt  # noqa: F401

# b_fxt = random_booking_in_db
b_fxt = booking_mock_db


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




# noinspection PyShadowingNames
@pytest.mark.asyncio
async def test_confirm_outbound(test_client, b_fxt):
    shipment_request_dict = jsonable_encoder(b_fxt.shipment_request)
    response = test_client.post('/api/confirm_booking', json=shipment_request_dict)
    resp_json = response.json()
    ship_resp = ShipmentResponse.model_validate(resp_json)

    assert response.status_code == 200
    assert isinstance(ship_resp, ShipmentResponse)


# noinspection PyShadowingNames
@pytest.mark.asyncio
async def test_confirm_away_collect(test_client, away_collect_fxt: ShipmentAwayCollectionConfigured):
    shipment_request_dict = jsonable_encoder(away_collect_fxt.shipment_request)
    response = test_client.post('/api/confirm_away_collect', json=shipment_request_dict)
    resp_json = response.json()
    ship_resp = ShipmentResponse.model_validate(resp_json)

    assert response.status_code == 200
    assert isinstance(ship_resp, ShipmentResponse)
    assert ship_resp.alerts is None


# noinspection PyShadowingNames
@pytest.mark.asyncio
async def test_confirm_away_dropoff(test_client, away_dropoff_fxt):
    shipment_request_dict = jsonable_encoder(away_dropoff_fxt.shipment_request)
    response = test_client.post('/api/confirm_away_dropoff', json=shipment_request_dict)
    resp_json = response.json()
    ship_resp = ShipmentResponse.model_validate(resp_json)

    assert response.status_code == 200
    assert isinstance(ship_resp, ShipmentResponse)
