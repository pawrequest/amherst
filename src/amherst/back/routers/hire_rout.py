# from __future__ import annotations
import base64

from fastui import AnyComponent, FastUI
from fastapi import APIRouter, Depends

from ...models import Hire, HireTable
from ...front import Page
from ...back import get_pfc, get_session
from shipr import PFCom

router = APIRouter()

PAGE_SIZE = 20


@router.get("/{hire_name_b64}", response_model=FastUI, response_model_exclude_none=True)
async def hire_view2(hire_name_b64: str, pf_com: PFCom = Depends(get_pfc)) -> list[AnyComponent]:
    hire_name = base64.urlsafe_b64decode(hire_name_b64).decode()
    hire = Hire.from_name(hire_name)
    return await Page.hire_address(hire, pf_com)


# @router.get("/{hire_id}", response_model=FastUI)
# async def hire_view3(
#         hire_id: int,
#         session=Depends(get_session),
#         pf_com: PFCom = Depends(get_pfc())
# ) -> list[AnyComponent]:
#     hire_tb = session.get(HireTable, hire_id)
#     hire = Hire.model_validate(hire_tb.model_dump())
#     return await Page.hire_address(hire, pf_com)

#
