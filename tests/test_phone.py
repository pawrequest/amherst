# from typing import Annotated
#
# import pytest
# from fastapi import FastAPI, Form
# from loguru import logger
# from pydantic import AfterValidator, BaseModel, BeforeValidator, Field, ValidationError
# from pydantic_extra_types.phone_numbers import PhoneNumber
# import phonenumbers
# from fastapi.testclient import TestClient
#
#
# def validate_phone(v: str, values) -> str:
#     logger.warning(f'Validating phone: {v}')
#     phone = v.replace(' ', '')
#     try:
#         nummy = phonenumbers.parse(phone, 'GB')
#         assert phonenumbers.is_valid_number(nummy)
#         return phonenumbers.format_number(nummy, phonenumbers.PhoneNumberFormat.E164)
#     except Exception:
#         ...
#         raise ValueError(f'Invalid phone number format: {phone}')
#
#
# UKPHONE = Annotated[str, Field(...), AfterValidator(validate_phone)]
#
#
# def validate_phone(phone: str):
#     nummy = phonenumbers.parse(phone, 'GB')
#     if not phonenumbers.is_valid_number(nummy):
#         print('Invalid phone number')
#         raise ValueError(f'Invalid phone number: {phone}')
#     return phone
#
#
# uphone = Annotated[PhoneNumber, BeforeValidator(validate_phone)]
#
#
# def test_pn():
#     anum = '+447878387844'
#     nummy = phonenumbers.parse(anum, 'GB')
#     assert phonenumbers.is_valid_number(nummy)
#     print(str(phonenumbers.format_number(nummy, phonenumbers.PhoneNumberFormat.NATIONAL)))
#
#
# def test_2():
#     my_number = phonenumbers.parse('07878867844', 'GB')
#     # print(carrier.name_for_number(my_number, 'en'))
#     uu = uphone('+447844')
#     print(uu)
#
#
# app = FastAPI()
#
#
# class User(BaseModel):
#     phone: UKPHONE
#
#
# @app.post('/users/')
# async def create_user(phone: UKPHONE = Form(...)):
#     ...
#     return {'phone': phone}
#
#
# client = TestClient(app)
#
#
# class UKPhoneNumber(PhoneNumber):
#     default_region_code = 'GB'
#
#
#
#
# def test_valid_uk_phone_number():
#     response = client.post('/users/', data={'phone': '+447878387844'})
#     assert response.status_code == 200
#     user = User(**response.json())
#     user = user.model_validate(user)
#     assert user.phone == '+447878387844'
#
#
# def test_valid_uk_phone_number2():
#     response = client.post('/users/', data={'phone': '07979147257'})
#     assert response.status_code == 200
#     user = User(**response.json())
#     user = user.model_validate(user)
#     assert user.phone == '+447979147257'
#     ...
#
#
# def test_invalid_uk_phone_number():
#     response = client.post('/users/', data={'phone': '+123456789'})
#     with pytest.raises(ValueError):
#         user = User(**response.json())
#         user = user.model_validate(user)
