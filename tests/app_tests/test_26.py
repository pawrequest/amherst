import pytest
import pytest_asyncio
from amherst_core.consts_enums import CategoryName
from amherst_core.models import AmherstCustomer
from asgi_lifespan import LifespanManager
from pycommence import PyCommence
from shipaw.models.shipment import Shipment

from amherst import app
from amherst.ui_runner import FapiState, get_pycommence_shipper_url, run_desktop_ui


@pytest.mark.asyncio
async def test_2(test_client):
    # assert response.status_code == 200, f'Expected status code 200, but got {response.status_code}'
    # assert response.template.name == r'ship/form_shape.html'
    # assert response.context['record'].name == record
    category = CategoryName.Customer
    record_name = 'Test'
    with PyCommence(category) as pycmc:
        row_data = pycmc.read_row(pk=record_name)
    customer = AmherstCustomer(row_id=row_data.row_id, **row_data.data)
    # customer_dict = customer.model_dump(mode='json')
    shipment = customer.shipment
    shipment_dict = shipment.model_dump(mode='json')
    # shippy = Shipment(**shipment_dict)
    # assert shippy

    state = FapiState(
        get_url=await get_pycommence_shipper_url(category, record_name),
        post_url='shipaw/shipping_form',
        post_body=shipment_dict,
    )
    response = test_client.post(url=state.post_url, json=state.post_body)
    print(response)


@pytest.mark.asyncio
async def test_it():
    category = CategoryName.Customer
    record_name = 'Test'
    with PyCommence(category) as pycmc:
        row_data = pycmc.read_row(pk=record_name)
    customer = AmherstCustomer(row_id=row_data.row_id, **row_data.data)
    # customer_dict = customer.model_dump(mode='json')
    shipment = customer.shipment
    shipment_dict = shipment.model_dump(mode='json')
    # shippy = Shipment(**shipment_dict)
    # assert shippy

    state = FapiState(
        get_url=await get_pycommence_shipper_url(category, record_name),
        post_url='shipaw/shipping_form',
        post_body=shipment_dict,
    )
    await run_desktop_ui(state)


# @pytest.mark.anyio
# async def test_n():
#     async with LifespanManager(app) as manager:
#         print("We're in!")
