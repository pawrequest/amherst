from collections.abc import Generator
from enum import Enum
from pprint import pprint

import pytest
import pytest_asyncio
from bs4 import BeautifulSoup
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from amherst.models.db_models import BookingStateDB
from shipaw.models.pf_shared import ServiceCode
from shipaw.models.pf_shipment_configured  import to_collection_configured, to_dropoff
from shipaw.ship_types import ShipDirection
from .client import test_client  # noqa: F401
from .fixtures_live import random_booking_in_db  # noqa: F401
from .fixtures_mock import FAKE_EMAIL, FAKE_PHONE, amrec_mock, booking_mock_db, booking_mock_fxt  # noqa: F401
from amherst.routes_test import PostForm


b_fxt = booking_mock_db

# @pytest.mark.usefixtures('booking_mock_db')
# @pytest_asyncio.fixture(scope='session')
# async def b_fxt() -> BookingStateDB:
#     return booking_mock_db


# b_fxt = random_booking_in_db

@pytest_asyncio.fixture(scope='session')
async def away_collect_fxt(b_fxt):
    return to_collection_configured(b_fxt.shipment_request)
    # return ShipmentAwayCollection.from_shipment(b_fxt.shipment_request)


@pytest_asyncio.fixture(scope='session')
async def away_dropoff_fxt(b_fxt: BookingStateDB):
    return to_dropoff(b_fxt.shipment_request)
    # return ShipmentAwayDropoff.from_shipment(b_fxt.shipment_request)


def test_health(test_client):
    response = test_client.get('/api/health/')
    assert response.status_code == 200
    assert response.json() == 'healthy'


@pytest.mark.asyncio
async def test_initial_booking_state(request, b_fxt: BookingStateDB):
    assert b_fxt.record
    assert b_fxt.shipment_request
    assert b_fxt.alerts
    assert len(b_fxt.alerts.alert) == 0


# noinspection PyShadowingNames
@pytest.mark.asyncio
async def customer_record(b_fxt: BookingStateDB):
    cust_rec = b_fxt.record.customer_record()
    assert cust_rec


@pytest.mark.asyncio
async def test_email_options(b_fxt: BookingStateDB):
    assert b_fxt.email_options
    assert b_fxt.email_options[0].delivery_contact_email
    ...


@pytest.mark.asyncio
async def test_recipient_address(b_fxt: BookingStateDB):
    assert b_fxt.shipment_request.recipient_address
    assert b_fxt.shipment_request.recipient_address.address_line1
    assert b_fxt.shipment_request.recipient_address.town
    assert b_fxt.shipment_request.recipient_address.postcode
    assert b_fxt.shipment_request.recipient_address.country


# noinspection PyUnusedLocal
@pytest.mark.asyncio
async def test_input_page(test_client, b_fxt: BookingStateDB):
    response = test_client.get(f'/{b_fxt.id}')
    response_text = response.text

    soup = BeautifulSoup(response_text, 'html.parser')
    assert soup.title.string == 'Amherst Shipper'
    assert soup.find('div', class_='shipper shipper__sandbox').string == 'Shipper in Sandbox Mode'
    assert not soup.find('div', class_='alert alert__')
    assert soup.find('input', {'type': 'hidden', 'name': 'booking_id'})['value'] == str(b_fxt.id)
    assert soup.find('input', {'id': 'ship_date'})['value'] == b_fxt.shipment_request.shipping_date.isoformat()
    assert (
            int(soup.find('select', {'id': 'boxes'}).find('option', {'selected': True})['value'])
            == b_fxt.shipment_request.total_number_of_parcels
    )
    # Check direction options
    assert (
            soup.find('select', {'id': 'direction'}).find('option', {'selected': True})[
                'value'] == ShipDirection.Outbound
    )
    # Check service_code options
    assert soup.find('select', {'id': 'service'}).find('option', {'selected': True})['value'] == ServiceCode.EXPRESS24
    # Check contact details
    # assert soup.find('input', {'id': 'business_name'})['value'] == contact_xmpl['business_name']
    # assert soup.find('input', {'id': 'contact_name'})['value'] == contact_xmpl['contact_name']
    assert soup.find('input', {'id': 'email'})['value'] == FAKE_EMAIL
    assert soup.find('input', {'id': 'mobile_phone'})['value'] == FAKE_PHONE

    # Check address details
    assert soup.find('input', {'id': 'address_line1'})
    assert soup.find('input', {'id': 'address_line2'})
    assert soup.find('input', {'id': 'address_line3'})
    assert soup.find('input', {'id': 'town'})
    assert soup.find('input', {'id': 'postcode'})['value'] == b_fxt.shipment_request.recipient_address.postcode

    # Check address select options
    # address_select = soup.find('select', {'id': 'address-select'})
    # options = address_select.find_all('option')
    # expected_options = [
    #     '{"AddressLine1":"752 MERESBOROUGH ROAD","AddressLine2":"RAINHAM","AddressLine3":"","Town":"GILLINGHAM","Postcode":"ME8 8SP","Country":"GB"}',
    #     '{"AddressLine1":"750 MERESBOROUGH ROAD","AddressLine2":"RAINHAM","AddressLine3":"","Town":"GILLINGHAM","Postcode":"ME8 8SP","Country":"GB"}',
    # ]
    # actual_options = [option['value'] for option in options]
    # assert all(option in actual_options for option in expected_options)

    # Check notes and special instructions
    assert soup.find('input', {'id': 'reference_number1'})['value'] == b_fxt.record.customer[:24]
    assert soup.find('input', {'id': 'reference_number2'})
    assert soup.find('input', {'id': 'reference_number3'})
    assert soup.find('input', {'id': 'special_instructions1'})
    assert soup.find('input', {'id': 'special_instructions2'})
    assert soup.find('input', {'id': 'special_instructions3'})
    assert soup.find('button', {'type': 'submit', 'class': 'submit-request'}).string == 'Submit'


def flatten_to_str_tups(data: dict) -> Generator[tuple[str, str], None, None]:
    for key, value in data.items():
        if isinstance(value, BaseModel):
            yield from flatten_to_str_tups(value.model_dump())
        if isinstance(value, dict):
            yield from flatten_to_str_tups(value)
        if isinstance(value, Enum):
            yield str(key), value.value
        else:
            yield str(key), str(value)


@pytest.mark.asyncio
async def test_post_form(test_client, b_fxt: BookingStateDB):
    form_data = b_fxt.shipment_request.model_dump()
    form_flat = dict(flatten_to_str_tups(form_data))
    form_flat['booking_id'] = b_fxt.id
    form_flat['direction'] = ShipDirection.Outbound
    valid_form = PostForm.model_validate(form_flat)
    json_form = jsonable_encoder(valid_form)
    assert valid_form
    pprint(valid_form)
    response = test_client.post('/test/post_form/', json=json_form)
    pprint(response.text)
    assert response.status_code == 200


@pytest.mark.asyncio
def test_dropoff_post(test_client, away_dropoff_fxt):
    form_data = away_dropoff_fxt.model_dump()
    form_flat = dict(flatten_to_str_tups(form_data))
    form_flat['booking_id'] = 1
    form_flat['direction'] = ShipDirection.Dropoff
    valid_form = PostForm.model_validate(form_flat)
    json_form = jsonable_encoder(valid_form)
    assert valid_form
