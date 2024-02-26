# from __future__ import annotations
from typing import Optional

from fastui import AnyComponent, FastUI, components as c
from fastapi import APIRouter, Depends
from loguru import logger

from amherst.back import get_pfc
from amherst.front.booking_ui import BookingUI
from amherst.front.state import ShipState
from amherst.shipping.pfcom import AmShipper

# from loguru import logger
#
# from amherst.front.booking_ui import BookingUI
# from amherst.front.state import ShipState
# from amherst.back import get_pfc
# from amherst.shipping.pfcom import AmShipper

router = APIRouter()



@router.get("/go/{state}", response_model=FastUI, response_model_exclude_none=True)
async def book(
        state: Optional[str] = None,
        pfcom: AmShipper = Depends(get_pfc),
) -> list[AnyComponent]:
    logger.info("booking")
    state = ShipState.model_validate_json(state)
    req = pfcom.state_to_shipment_request(state)
    resp = pfcom.get_shipment_resp(req)
    state.request = req
    state.response = resp

    ui = BookingUI(pfcom=pfcom, state=state)
    page = await ui.get_page()
    return page

# @router.get("/go", response_model=FastUI, response_model_exclude_none=True)
# async def book(
#         state: Optional[str] = None,
#         pf_com: AmShipper = Depends(get_pfc),
# ) -> list[AnyComponent]:
#     logger.info("go2")
#     if not state:
#         raise ValueError("state is required")
#     state = ShipState.model_validate_json(state)
#     ui = BookingUI(pfcom=pf_com, state=state)
#     page = await ui.get_page()
#     return page
