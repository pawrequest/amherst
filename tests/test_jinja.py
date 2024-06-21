from enum import Enum
from pprint import pprint
from typing import Generator
from starlette.testclient import _RequestData
import pytest
from bs4 import BeautifulSoup
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from suppawt.compare import flatten_generic

from amherst.models.db_models import BookingStateDB
from shipaw.models.pf_shared import ServiceCode
from shipaw.ship_types import ShipDirection
from .fixtures_mock import FAKE_EMAIL, FAKE_PHONE
from amherst.routes import PostForm


def test_health(test_client):
    response = test_client.get('/api/health/')
    assert response.status_code == 200
    assert response.json() == 'healthy'


@pytest.mark.asyncio
async def test_initial_booking_state(request, random_booking: BookingStateDB):
    assert random_booking
    assert random_booking.record
    assert random_booking.shipment_request
    assert random_booking.alerts
    assert len(random_booking.alerts.alert) == 0
    cust_rec = random_booking.record.customer_record()
    assert cust_rec


@pytest.mark.asyncio
async def test_email_options(random_booking: BookingStateDB):
    assert random_booking.email_options
    assert random_booking.email_options[0].email
    ...


@pytest.mark.asyncio
async def test_recipient_address(random_booking: BookingStateDB):
    assert random_booking.shipment_request.recipient_address
    assert random_booking.shipment_request.recipient_address.address_line1
    assert random_booking.shipment_request.recipient_address.town
    assert random_booking.shipment_request.recipient_address.postcode
    assert random_booking.shipment_request.recipient_address.country


@pytest.mark.asyncio
async def test_input_page(test_client, random_booking_in_db: BookingStateDB):
    response = test_client.get(f'/{random_booking_in_db.id}')
    response_text = response.text

    soup = BeautifulSoup(response_text, 'html.parser')
    assert soup.title.string == 'Amherst Shipper'
    assert soup.find('div', class_='shipper shipper__sandbox').string == 'Shipper in Sandbox Mode'
    assert not soup.find('div', class_='alert alert__')
    assert soup.find('input', {'type': 'hidden', 'name': 'booking_id'})['value'] == str(random_booking_in_db.id)
    assert (
        soup.find('input', {'id': 'ship_date'})['value']
        == random_booking_in_db.shipment_request.shipping_date.isoformat()
    )
    assert (
        int(soup.find('select', {'id': 'total_number_of_parcels'}).find('option', {'selected': True})['value'])
        == random_booking_in_db.shipment_request.total_number_of_parcels
    )
    # Check direction options
    assert (
        soup.find('select', {'id': 'direction'}).find('option', {'selected': True})['value'] == ShipDirection.Outbound
    )
    # Check service_code options
    assert (
        soup.find('select', {'id': 'service_code'}).find('option', {'selected': True})['value'] == ServiceCode.EXPRESS24
    )
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
    assert (
        soup.find('input', {'id': 'postcode'})['value']
        == random_booking_in_db.shipment_request.recipient_address.postcode
    )

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
    assert soup.find('input', {'id': 'reference_number1'})['value'] == random_booking_in_db.record.customer[:24]
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
async def test_post_form(test_client, random_booking_in_db: BookingStateDB):
    form_data = random_booking_in_db.shipment_request.model_dump()
    form_flat = dict(flatten_to_str_tups(form_data))
    form_flat['booking_id'] = random_booking_in_db.id
    form_flat['direction'] = ShipDirection.Outbound
    valid_form = PostForm.model_validate(form_flat)
    json_form = jsonable_encoder(valid_form)
    assert valid_form
    pprint(valid_form)
    response = test_client.post('/post_form2/', data=json_form)
    pprint(response.text)
    assert response.status_code == 200
