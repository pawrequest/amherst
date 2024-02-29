from __future__ import annotations as _annotations

import enum
from typing import Annotated

from fastapi import APIRouter
from fastui import FastUI, components as c
from fastui.events import GoToEvent
from fastui.forms import fastui_form
from pydantic import BaseModel, Field

router = APIRouter()


# class BoxesEnum(str, enum.Enum):
#     ONE = '1'
#     TWO = '2'
#     THREE = '3'
#     FOUR = '4'
#     FIVE = '5'
#     SIX = '6'
#     SEVEN = '7'
#     EIGHT = '8'
#     NINE = '9'
#     TEN = '10'
#
#
# class BoxesForm(BaseModel):
#     boxes_select: BoxesEnum = Field(
#         title='Number of Boxes',
#         description='Select the number of boxes to ship'
#     )


# @router.post('/boxes', response_model=FastUI, response_model_exclude_none=True)
# async def select_form_post(form: Annotated[BoxesForm, fastui_form(BoxesForm)]):
#     print(form)
#     return [c.FireEvent(event=GoToEvent(url='/hire/id2/5'))]


# def make_address_enum(candidates: list):
#     return enum.Enum('AddressEnum', {f'address_{i}': addr for i, addr in enumerate(candidates)})
#
#
# addr_enum = make_address_enum(['address1', 'address2', 'address3', 'address4', 'address5'])
#
#
# class AnEnum(enum.Enum):
#     a = 'a'
#     b = 'b'
#     c = 'c'
#
#
# class AddressSelectReq(BaseModel):
#     address: AnEnum = Field(title='Choose Address')
#
#
# class AddressSelectResp(BaseModel):
#     selected: str
#
#
# @router.post('/select2', response_model=AddressSelectResp, response_model_exclude_none=True)
# async def select_fm_2(form: Annotated[AddressSelectReq, fastui_form(AddressSelectReq)]):
#     print(form)
#
#
# @router.post('/select', response_model=AddressSelectResp, response_model_exclude_none=True)
# async def login_form_post(form: Annotated[AddressSelectReq, fastui_form(AddressSelectReq)]):
#     print(form)
#     return AddressSelectResp(selected=form.address.value)
#
#     # return [SelectResult(selected='estsdf')]
