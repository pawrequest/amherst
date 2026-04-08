"""Wrap FastAPI app in FlaskWebGUI for desktop application."""

from __future__ import annotations

from amherst_core.consts_enums import CategoryName
from flaskwebgui import FlaskUI, close_application
from pycommence import PyCommence
from pycommence.core.row_data import RowData
from shipaw.config import FapiConfig
from shipaw.logging import log_obj_text

from amherst.app import app


async def run_desktop_ui(config: FapiConfig):
    # app = create_app(amherst_settings=AmherstSettings.from_env(), shipaw_settings=ShipawSettings.from_env())
    app.state.config = config

    try:
        FlaskUI(
            fullscreen=True,
            app=app,
            server='fastapi',
            port=config.port,
            app_mode=False,
        ).run()
    finally:
        close_application()


async def run_desktop_add_state(category: str, row_id: str, config: FapiConfig):
    #  did this fix callback issue? but means two apps?! #  app = create_app(amherst_settings=AmherstSettings.from_env(), shipaw_settings=ShipawSettings.from_env())
    app.state.config = config
    app.state.category = category
    app.state.row_id = row_id

    try:
        FlaskUI(
            fullscreen=True,
            app=app,
            server='fastapi',
            port=config.port,
            app_mode=False,
        ).run()
    finally:
        close_application()


async def run_shipper(category: CategoryName, record_name: str):
    row_data = await row_from_pycommence(category, record_name)
    mdl = row_data.construct_model()
    # mdl = cast(AmherstShipableBase, mdl)
    shipment = mdl.shipment()
    # shipment.context = {mdl.model_dump(mode='json')}

    shipment_dict = shipment.model_dump(mode='json')
    log_obj_text(shipment, 'Initial Shipment', level='INFO')
    config = FapiConfig(
        post_body=shipment_dict,
        url_for_='shipping_form',
        context={'category': category, 'record_name': record_name},
    )
    await run_desktop_add_state(category, mdl.row_id, config)


# async def get_shipment_from_pycommence(category: CategoryName, record_name: str) -> Any:
#     row_data = await row_from_pycommence(category, record_name)
#     mdl = row_data.construct_model()
#     shipment = mdl.shipment()  # noqa:
#     shipment.context = {mdl.model_dump(mode='json')}
#     return shipment


async def row_from_pycommence(category: CategoryName, record_name: str) -> RowData:
    with PyCommence(category) as pycmc:
        return pycmc.read_row(pk=record_name)


REVIEW_URL = r'/shipaw/order_review_am'
CONFIRM_URL = r'/shipaw/post_confirm_am'

if __name__ == '__main__':
    import asyncio

    asyncio.run(run_shipper(CategoryName.Customer, 'Test'))
