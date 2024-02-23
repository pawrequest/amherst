# from __future__ import annotations
import base64
from enum import Enum

from fastui import AnyComponent, FastUI, components as c
from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel

from amherst.back.database import get_session
from amherst.front import pages
from amherst.front.hire_api import Page
from amherst.models import Hire, HireTable
from amherst.back import get_pfc
from amherst.shipping.pfcom import AmShipper
from shipr.express.types import AddressPF

router = APIRouter()


def make_address_enum(candidates):
    return Enum('AddressEnum', {f'address_{i}': addr for i, addr in enumerate(candidates)})


def make_select_form(candidates):
    addr_enum = make_address_enum(candidates)
    return



# class SelectForm(BaseModel):
#     address: addr_enum = Field(title='Choose Address')


# @router.post('/address-chooser', response_model=FastUI, response_model_exclude_none=True)
# async def address_chooser_modal(candidates: AddressCandidates) -> list[AnyComponent]:
#     return [
#         c.Button(text=can.address_line1) for can in candidates.candidates
#     ]


@router.get("/id/{hire_id}", response_model=FastUI, response_model_exclude_none=True)
async def hire_view_id(
        hire_id: int,
        session=Depends(get_session),
        pf_com: AmShipper = Depends(get_pfc)
) -> list[AnyComponent]:
    logger.info(f"hire_id: {hire_id}")
    hire_tb = session.get(HireTable, hire_id)
    hire = Hire.model_validate(hire_tb.model_dump())
    return await Page.hire_address(hire, pf_com)


@router.get("/{hire_name_b64}", response_model=FastUI, response_model_exclude_none=True)
async def hire_view_name_b64(hire_name_b64: str, pf_com: AmShipper = Depends(get_pfc)) -> list[
    AnyComponent]:
    logger.info(f"hire_name_b64: {hire_name_b64}")
    hire_name = base64.urlsafe_b64decode(hire_name_b64).decode()
    hire = Hire.from_name(hire_name)
    pg = await Page.hire_address(hire, pf_com)
    return pg
