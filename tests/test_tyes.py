import pytest
from bs4 import BeautifulSoup

from amherst.models.db_models import BookingStateDB
from shipaw.models.pf_shared import ServiceCode
from shipaw.ship_types import ShipDirection, WEEKDAYS_IN_RANGE

SHIP_DATE = min(WEEKDAYS_IN_RANGE).strftime('%Y-%m-%d')


@pytest.mark.asyncio
async def test_initial_booking_state(booking_fxt):
    assert booking_fxt
    assert booking_fxt.record
    assert booking_fxt.shipment_request
    assert booking_fxt.alerts
    # assert booking_fxt.alerts.alert[0].message == 'Created'
    assert len(booking_fxt.alerts.alert) == 0
    cust_rec = booking_fxt.record.customer_record()
    assert cust_rec


@pytest.mark.asyncio
async def test_email_options(booking_fxt):
    assert booking_fxt.email_options
    assert booking_fxt.email_options[0].email
    ...


@pytest.mark.asyncio
async def test_recipient_address(booking_fxt):
    assert booking_fxt.shipment_request.recipient_address
    assert booking_fxt.shipment_request.recipient_address.address_line1
    assert booking_fxt.shipment_request.recipient_address.town
    assert booking_fxt.shipment_request.recipient_address.postcode
    assert booking_fxt.shipment_request.recipient_address.country


def test_health(client):
    response = client.get('/api/health/')
    assert response.status_code == 200
    assert response.json() == 'healthy'


@pytest.mark.asyncio
async def test_booking_api(client, booking_fxt, address_fxt, contact_fxt):
    response = client.get(f'/api/{booking_fxt.id}')
    assert response.status_code == 200
    booking_json = response.json()
    booking = BookingStateDB.model_validate(booking_json)
    assert booking.remote_contact.contact_name == contact_fxt.contact_name
    assert booking.remote_address.postcode == address_fxt.postcode
    assert booking.remote_address.country == address_fxt.country


@pytest.mark.asyncio
async def test_soup(client, booking_fxt, address_fxt, contact_fxt):
    response = client.get(f'/{booking_fxt.id}')
    response_text = response.text

    soup = BeautifulSoup(response_text, 'html.parser')
    assert soup.title.string == 'Amherst Shipper'
    assert soup.find('div', class_='shipper shipper__sandbox').string == 'Shipper in Sandbox Mode'

    # assert soup.find('div', class_='alert alert__')

    assert booking_fxt.record.name in soup.find('h1').string

    assert soup.find('input', {'type': 'hidden', 'name': 'booking_id'})['value'] == str(
        booking_fxt.id
    )

    # Check shipment details
    assert soup.find('input', {'id': 'ship_date'})['value'] == SHIP_DATE

    assert soup.find('select', {'id': 'boxes'}).find('option', {'selected': True})['value'] == '1'

    # Check direction options
    assert soup.find('select', {'id': 'direction'}).find('option', {'selected': True})[
               'value'] == ShipDirection.OUT

    # Check service options
    assert soup.find('select', {'id': 'service'}).find('option', {'selected': True})[
               'value'] == ServiceCode.EXPRESS24

    # Check contact details
    assert soup.find('input', {'id': 'business_name'})['value'] == contact_fxt.business_name

    assert soup.find('input', {'id': 'contact_name'})['value'] == contact_fxt.contact_name

    assert soup.find('input', {'id': 'email'})['value'] == 'fake@ssgslgjhslagjnhlsgnhl.com'

    assert soup.find('input', {'id': 'mobile_phone'})['value'] == contact_fxt.mobile_phone

    # Check address details
    assert soup.find('input', {'id': 'address_line1'})

    assert soup.find('input', {'id': 'address_line2'})

    assert soup.find('input', {'id': 'address_line3'})

    assert soup.find('input', {'id': 'town'})

    assert soup.find('input', {'id': 'postcode'})['value'] == address_fxt.postcode

    # Check address select options
    address_select = soup.find('select', {'id': 'address-select'})
    options = address_select.find_all('option')
    expected_options = [
        '{"AddressLine1":"752 MERESBOROUGH ROAD","AddressLine2":"RAINHAM","AddressLine3":"","Town":"GILLINGHAM","Postcode":"ME8 8SP","Country":"GB"}',
        '{"AddressLine1":"750 MERESBOROUGH ROAD","AddressLine2":"RAINHAM","AddressLine3":"","Town":"GILLINGHAM","Postcode":"ME8 8SP","Country":"GB"}',
        # Add all expected options here...
    ]
    actual_options = [option['value'] for option in options]
    assert all(option in actual_options for option in expected_options)

    # Check notes and special instructions
    assert soup.find('input', {'id': 'reference_number1'})['value'] == booking_fxt.record.customer

    assert soup.find('input', {'id': 'reference_number2'})

    assert soup.find('input', {'id': 'reference_number3'})

    assert soup.find('input', {'id': 'special_instructions1'})

    assert soup.find('input', {'id': 'special_instructions2'})

    assert soup.find('input', {'id': 'special_instructions3'})

    assert soup.find('button', {'type': 'submit', 'class': 'submit-request'}).string == 'Submit'
