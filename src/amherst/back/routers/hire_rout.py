# from __future__ import annotations
import base64

from fastui import AnyComponent, FastUI
from fastapi import APIRouter, Depends
from loguru import logger

from .. import get_session
from ...models import Hire, HireTable
from ...front import Page
from ...back import get_pfc
from shipr import PFCom

router = APIRouter()


@router.get("/id/{hire_id}", response_model=FastUI, response_model_exclude_none=True)
async def hire_view_id(
        hire_id: int,
        session=Depends(get_session),
        pf_com: PFCom = Depends(get_pfc)
) -> list[AnyComponent]:
    logger.info(f"hire_id: {hire_id}")
    hire_tb = session.get(HireTable, hire_id)
    hire = Hire.model_validate(hire_tb.model_dump())
    return await Page.hire_address(hire, pf_com)


@router.get("/{hire_name_b64}", response_model=FastUI, response_model_exclude_none=True)
async def hire_view_name_b64(hire_name_b64: str, pf_com: PFCom = Depends(get_pfc)) -> list[
    AnyComponent]:
    logger.info(f"hire_name_b64: {hire_name_b64}")
    hire_name = base64.urlsafe_b64decode(hire_name_b64).decode()
    hire = Hire.from_name(hire_name)
    pg = await Page.hire_address(hire, pf_com)
    return pg
