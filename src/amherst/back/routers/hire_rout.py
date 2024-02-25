# from __future__ import annotations
from typing import Optional

from fastui import AnyComponent, FastUI, components as c
from fastapi import APIRouter, Depends
from loguru import logger

from amherst.back.database import get_session
# from amherst.front.hire_api import HireUI
from amherst.front.hire_ui import HireUI as HireUI
# from amherst.front.hire_api2 import HireUI as HireUI2
from amherst.models import HireDB
from amherst.back import get_pfc
from amherst.models.hire_in import HireIn
from amherst.shipping.pfcom import AmShipper
from shipr.express import types as elt

router = APIRouter()


@router.get("/id2/{hire_id}", response_model=FastUI, response_model_exclude_none=True)
async def hire_view_id2(
        hire_id: int,
        session=Depends(get_session),
        pf_com: AmShipper = Depends(get_pfc),
        state: Optional[HireUI] = None
) -> list[AnyComponent]:
    logger.info(f"hire_id: {hire_id}")
    hire_tb = session.get(HireDB, hire_id)
    hire = HireIn.model_validate(hire_tb.model_dump())
    ui = HireUI(source_model=hire, pfcom=pf_com, state=state)
    page = await ui.get_page()
    return page


#
# @router.get("/id/{hire_id}", response_model=FastUI, response_model_exclude_none=True)
# async def hire_view_id(
#         hire_id: int,
#         session=Depends(get_session),
#         pf_com: AmShipper = Depends(get_pfc)
# ) -> list[AnyComponent]:
#     logger.info(f"hire_id: {hire_id}")
#     hire_tb = session.get(HireDB, hire_id)
#     hire = Hire.model_validate(hire_tb.model_dump())
#     hire_ui = HireUI(hire=hire, pfcom=pf_com)
#     return await hire_ui.hire_page()
#
#
# @router.get("/{hire_name_b64}", response_model=FastUI, response_model_exclude_none=True)
# async def hire_view_name_b64(hire_name_b64: str, pf_com: AmShipper = Depends(get_pfc)) -> list[
#     AnyComponent]:
#     logger.info(f"hire_name_b64: {hire_name_b64}")
#     hire_name = base64.urlsafe_b64decode(hire_name_b64).decode()
#     hire = Hire.from_name(hire_name)
#     hire_ui = HireUI(hire=hire, pfcom=pf_com)
#     return await hire_ui.hire_page()


@router.post('/address-chooser', response_model=FastUI, response_model_exclude_none=True)
async def address_chooser_post(candidates: list[elt.AddressPF]) -> list[AnyComponent]:
    return [
        c.Button(text=can.address_line1) for can in candidates
    ]
