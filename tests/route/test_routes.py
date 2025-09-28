import pytest
from pawdantic.paw_types import pydantic_export

from amherst.models.amherst_models import AMHERST_TABLE_MODELS
from amherst.models.commence_adaptors import CategoryName
from amherst.ui_runner import CONFIRM_URL, REVIEW_URL, get_shipper_url
from shipaw.models.provider import PROVIDER_REGISTER

PK_SEARCH = 'amps'
CSRNAME = 'Hire'

@pytest.fixture(scope='session', params=[_() for _ in PROVIDER_REGISTER.values()], ids=[_ for _ in PROVIDER_REGISTER.keys()])
def provider(request):
    yield request.param

@pytest.mark.asyncio
async def test_ship_form(test_client):
    category = CategoryName.Customer
    record = 'Test'
    shipper_url = await get_shipper_url(category, record)
    response = test_client.get(shipper_url)
    assert response.status_code == 200, f'Expected status code 200, but got {response.status_code}'
    assert response.template.name == r'ship/form_shape.html'
    assert response.context['record'].name == record


@pytest.fixture(scope='session')
def order_review_sample(provider, amherst_customer, test_client, request):
    record_str = amherst_customer.model_dump_json()
    ship = amherst_customer.shipment()
    ship = pydantic_export(ship, mode='pydantic')

    form_data = {
        **ship.recipient.address.model_dump(),
        **ship.recipient.address.get_address_lines_dict(),
        **ship.recipient.contact.model_dump(),
        'direction': ship.direction,
        'shipping_date': ship.shipping_date.isoformat(),
        'boxes': ship.boxes,
        'service': ship.service,
        'reference': ship.reference,
        'record_str': record_str,
        'provider_name': provider.name,
    }

    # Send POST request with form data
    response = test_client.post(REVIEW_URL, data=form_data)
    return response


def test_order_review(order_review_sample):
    # Assertions
    assert (
        order_review_sample.status_code == 200
    ), f'Expected status code 200, but got {order_review_sample.status_code}'
    assert order_review_sample.template.name == 'ship/order_review.html'
    assert isinstance(order_review_sample.context['record'], AMHERST_TABLE_MODELS)


def test_order_confirm(test_client, order_review_sample):
    shipreq = order_review_sample.context['shipment_request']
    shipreq_str = shipreq.model_dump_json()
    rec_str = order_review_sample.context['record'].model_dump_json()
    data = {
        'shipment_req_str': shipreq_str,
        'record_str': rec_str,
    }
    resp = test_client.post(CONFIRM_URL, data=data)
    assert resp.context['response'].success is True
    assert resp.context['response'].label_path.exists()

