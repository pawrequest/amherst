"""Wrap FastAPI app in FlaskWebGUI for desktop application."""

from __future__ import annotations

from typing import NamedTuple

from amherst_core.consts_enums import CategoryName
from amherst_core.models import AmherstCustomer
from flaskwebgui import FlaskUI, close_application
from jinja2.utils import url_quote
from loguru import logger
from pycommence import PyCommence
from pydantic import BaseModel
from shipaw.logging import log_obj_text

from amherst import app


class FapiState(BaseModel):
    get_url: str = ''
    port: int = 8000
    post_url: str = ''
    post_body: dict = {}
    url_for_: str = ''


async def run_desktop_ui(state: FapiState):
    app.app.fapi_state = state

    try:
        FlaskUI(
            fullscreen=True,
            app=app.app,
            server='fastapi',
            port=state.port,
            app_mode=False,
        ).run()
    finally:
        close_application()


#
#
# async def run_desktop_ui(state: FapiState):
#     app.app.starting_url = state.url_suffix
#     app.app.fapi_state = state
#
#     try:
#         logger.info(f'Running WebFlaskUI @url={state.url_suffix}')
#         FlaskUI(
#             fullscreen=True,
#             app=app.app,
#             server='fastapi',
#             port=state.port,
#             app_mode=False,
#         ).run()
#     finally:
#         close_application()
#


async def pycommence_shipper(category: CategoryName, record_name: str):
    state = FapiState(get_url=await get_pycommence_shipper_url(category, record_name))
    await run_desktop_ui(state)


async def run_test():
    category = CategoryName.Customer
    record_name = 'Test'
    with PyCommence(category) as pycmc:
        row_data = pycmc.read_row(pk=record_name)
    customer = AmherstCustomer(row_id=row_data.row_id, **row_data.data)
    shipment = customer.shipment
    shipment_dict = shipment.model_dump(mode='json')
    log_obj_text(shipment, 'Test Shipment', level='INFO')

    state = FapiState(
        post_url='shipaw/shipping_form',
        post_body=shipment_dict,
        url_for_='shipping_form',
    )
    await run_desktop_ui(state)


async def get_pycommence_shipper_url(category: CategoryName, record_name: str) -> str:
    return f'shipaw/ship_form_am2?csrname={url_quote(category)}&pk_value={url_quote(record_name)}&condition=equal&max_rtn=1'


REVIEW_URL = r'/shipaw/order_review_am'
CONFIRM_URL = r'/shipaw/post_confirm_am'

if __name__ == '__main__':
    import asyncio

    asyncio.run(run_test())
