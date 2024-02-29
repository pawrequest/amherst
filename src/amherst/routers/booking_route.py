# from __future__ import annotations
import os

from fastapi import APIRouter, Depends
from fastui import AnyComponent, FastUI, components as c
from loguru import logger

from amherst.front import amui
from amherst.front.pages import PrintedPage
from shipr.models.booked_state import BookedState
from amherst.database import get_pfc, get_session
from amherst.shipper import AmShipper

router = APIRouter()


@router.get("/dummy/")
async def dummy_page() -> list[AnyComponent]:
    print("pbboking opsted")
    return amui.Page.default_page(c.Text(text="dummy"))


# @router.get("/bs/1/")
# def someshit():
#     return [c.FireEvent(event=GoToEvent(url="/book/dummy/"))]


@router.get("/bs/{state}")
async def bs(
    state: str,
    pfcom: AmShipper = Depends(get_pfc),
) -> str:
    logger.info(f"state: {state}")
    # state = BookingState.model_validate_json(state)
    # state = BookingState.model_validate(query)
    # req = pfcom.b_state_to_shipment_request(state)
    # resp = pfcom.get_shipment_resp(req)
    #
    # book_state = BookedState(hire_id=state.hire_id, request=req, response=resp)
    # ui = BookingPage(pfcom=pfcom, state=book_state)
    # # return await ui()
    # return await ui.get_page()
    # return await dummy_page()
    return "ok"


#
#
# @router.post("/book-form/")
# async def book(form: Annotated[BookingForm, fastui_form(BookingForm)]):
#     logger.info("book form")
#     print(form)
#     return [c.FireEvent(event=GoToEvent(url="/book/dummy/"))]
#
#
# @router.get("/posted/")
# async def posted() -> list[AnyComponent]:
#     return amui.Page.default_page(c.Text(text="posted"))


# @router.post("/posty/")
# async def book(form: Annotated[StartingForm, fastui_form(StartingForm)]):
#     logger.info("posting")
#     print(form)
#     return [c.FireEvent(event=GoToEvent(url="/book/posted/"))]


# @router.post("/post/")
# async def book(state: StartingState, pfcom: AmShipper = Depends(get_pfc)) -> BookedState:
#     logger.info("posting")
#     print("SHIPSTATE", state)
#
#     req = pfcom.state_to_shipment_request(state)
#     resp = pfcom.get_shipment_resp(req)
#     booked = BookedState(hire_id=state.hire_id, request=req, response=resp)
#     booked.request = req
#     booked.response = resp
#     return booked


# @router.get("/go{state}", response_model=FastUI, response_model_exclude_none=True)
# async def book(
#     state: str,
#     pfcom: AmShipper = Depends(get_pfc),
# ) -> list[AnyComponent]:
#     logger.info(f"booking state: {state}")
#     # state = BookingState.model_validate_json(state)
#     req = pfcom.b_state_to_shipment_request(state)
#     resp = pfcom.get_shipment_resp(req)
#
#     book_state = BookedState(hire_id=state.hire_id, request=req, response=resp)
#     ui = BookingPage(pfcom=pfcom, state=book_state)
#     # return await ui()
#     return await ui.get_page()


@router.get("/print/{state}", response_model=FastUI, response_model_exclude_none=True)
async def print_label(state: str, pfcom=Depends(get_pfc), session=Depends(get_session)):
    state = BookedState.model_validate_json(state)
    shipment_number = state.shipment_num()

    state.label_path = pfcom.get_label(shipment_number)
    session.add(state)
    session.commit()
    os.startfile(state.label_path)

    ui = PrintedPage(state=state)
    return await ui.get_page()
