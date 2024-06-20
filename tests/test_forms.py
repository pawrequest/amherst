# import datetime
# from typing import Annotated
#
# from pawdantic.pawsql import required_json_field
# from pydantic import BaseModel, BeforeValidator
# from fastapi import Depends, FastAPI, Request
# import pytest
# from fastapi.testclient import TestClient
#
# from shipaw.models.pf_models import AddressCollection, AddressRecipient
# from shipaw.models.pf_shared import ServiceCode
# from .test_pycommence_mock import contact_fxt, address_fxt
#
# def before_validate_int(value: int) -> int:
#     raise ValueError('before int')
#
#
# # MyInt = Annotated[int, BeforeValidator(before_validate_int)]
#
# app = FastAPI()
#
#
# @pytest.fixture(scope='session')
# def client():
#     with TestClient(app) as client:
#         yield client
#
#
# def validate_date(v: str):
#     if datetime.date.fromisoformat(v) < datetime.date.today():
#         raise ValueError('shipping date cannot be in the past')
#
#
# ShipDate = Annotated[datetime.date, BeforeValidator(validate_date)]
#
#
# # @as_form
# class Contact(BaseModel):
#     business_name: str
#     mobile_phone: str
#     email_address: str
#
#
# class Shipment(BaseModel):
#     recipient_contact: Contact
#     recipient_address: AddressRecipient | AddressCollection
#     total_number_of_parcels: int = 1
#     shipping_date: ShipDate
#     service_code: ServiceCode = ServiceCode.EXPRESS24
#
#
# @app.post('/shipment')
# def shipment(request: Request, input_shipment: Shipment = Depends(Shipment)) -> dict[str, str]:
#     return {'shipment': input_shipment.model_dump_json()}
#
#
# async def contact_from_form(request: Request) -> Contact:
#     form_ = await request.form()
#     contact_dict = {form_[k]: form_[v] for k, v in form_ if k in Contact.model_fields}
#     return Contact.model_validate(contact_dict)
#
#
# @app.post('/contact')
# def contact_post(request: Request, contact: Contact = Depends(contact_from_form)) -> dict[str, str]:
#     return {'contact': contact.model_dump_json()}
#
#
# def test_contact_post(client):
#     response = client.post(
#         '/contact', data=contact_fxt().model_dump()
#     )
#     ...
#
#
# def test_shipment_post(client):
#     response = client.post(
#         '/shipment', data={
#             'shipping_date': datetime.date(2024, 6, 20).isoformat(),
#             'recipient_contact': contact_fxt().model_dump(),
#             'recipient_address': address_fxt().model_dump(),
#         }
#     )
#     print(response.json())
#     assert response.status_code == 200
#
#
# """
# def before_validate_int(value: int) -> int:
#     raise ValueError('before int')
#
#
# MyInt = Annotated[int, BeforeValidator(before_validate_int)]
#
#
# @as_form
# class User(BaseModel):
#     age: MyInt
#
#
# @app.post('/postdata')
# def postdata(user: User = Depends(User)):
#     return {'age': user.age}
#
#
# def test_postdata(client):
#     response = client.post('/postdata', data={'age': 42})
#     assert response.status_code == 422
#     assert response.content == b'{"detail":[{"type":"value_error","loc":["body","age"],"msg":"Value error, before int","input":"42","ctx":{"error":{}}}]}'
# """
