from __future__ import annotations as _annotations

import enum
from typing import Annotated

from fastapi import APIRouter
from fastui.forms import fastui_form
from pydantic import BaseModel, Field

router = APIRouter()


def make_address_enum(candidates: list):
    return enum.Enum('AddressEnum', {f'address_{i}': addr for i, addr in enumerate(candidates)})


addr_enum = make_address_enum(['address1', 'address2', 'address3', 'address4', 'address5'])


class AnEnum(enum.Enum):
    a = 'a'
    b = 'b'
    c = 'c'


class AddressSelectReq(BaseModel):
    address: AnEnum = Field(title='Choose Address')


class AddressSelectResp(BaseModel):
    selected: str


@router.post('/select2', response_model=AddressSelectResp, response_model_exclude_none=True)
async def select_fm_2(form: Annotated[AddressSelectReq, fastui_form(AddressSelectReq)]):
    print(form)


@router.post('/select', response_model=AddressSelectResp, response_model_exclude_none=True)
async def login_form_post(form: Annotated[AddressSelectReq, fastui_form(AddressSelectReq)]):
    print(form)
    return AddressSelectResp(selected=form.address.value)

    # return [SelectResult(selected='estsdf')]
