import contextlib

from fastapi import FastAPI, responses
from fastapi.exceptions import RequestValidationError
from loguru import logger
from pawlogger import configure_loguru
from pydantic import BaseModel
from shipaw.config import SHIPAW_SETTINGS, ShipawSettings, populate_providers
from shipaw.fapi.alerts import Alerts
from shipaw.fapi.app import request_validation_exception_handler
from shipaw.fapi.app_custom import AppSettings as AppSettings_
from shipaw.fapi.log_stream import LogStream
from shipaw.fapi.routes_api import router as shipaw_json_router
from shipaw.fapi.routes_html import router as shipaw_html_router
from shipaw.fapi.routes_html import shipping_form
from shipaw.models.shipment import Shipment
from starlette.datastructures import State
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles

from amherst.app_custom import AmherstApp, AmherstRequest, AppSettings, AppState
from amherst.config import AMHERST_SETTINGS, AmherstSettings
from amherst.ui_runner import FapiState


def create_app(amherst_settings: AmherstSettings, shipaw_settings: ShipawSettings):
    app_ = AmherstApp()

    # state
    app_.state = AppState.create()

    # routing
    app_.mount('/static', StaticFiles(directory=str(shipaw_settings.static_dir)), name='static')
    app_.include_router(shipaw_json_router, prefix='/api')
    app_.include_router(shipaw_html_router)
    # app_.include_router(shipaw_json_router, prefix='/shipaw/api')
    # app_.include_router(shipaw_html_router, prefix='/shipaw')

    # logging
    configure_loguru(logger_=logger, log_file=amherst_settings.log_file, level=amherst_settings.log_level)
    logger.add(app_.state.log_stream.sink, level='DEBUG', enqueue=False)

    # init
    populate_providers(shipaw_settings)
    return app_


app = create_app(amherst_settings=AmherstSettings.from_env(), shipaw_settings=ShipawSettings.from_env())


@app.exception_handler(RequestValidationError)
async def request_exception_handler(request: AmherstRequest, exc: RequestValidationError):
    return await request_validation_exception_handler(request, exc)


@app.get('/robots.txt', response_class=responses.PlainTextResponse)
async def robots_txt() -> str:
    return 'User-agent: *\nAllow: /'


@app.get('/favicon.ico', include_in_schema=False)
async def favicon_ico():
    return responses.RedirectResponse(url='/static/favicon.svg')


@app.get('/base', response_class=HTMLResponse)
async def base(
    request: Request,
):
    return AMHERST_SETTINGS.templates.TemplateResponse('base.html', {'request': request})


@app.get('/', response_class=RedirectResponse)
async def startup(
    request: AmherstRequest,
):
    fapi_state: FapiState = getattr(request.app, 'fapi_state', None)
    url = request.url_for('shipping_form')
    if fapi_state:
        if fapi_state.post_url and fapi_state.post_body:
            shipment = Shipment(**fapi_state.post_body)
            res = await shipping_form(request, shipment=shipment)
            return res
        # if fapi_state.url_post:
        #     url, data = fapi_state.url_post.items()
    return RedirectResponse('/base')


@app.get('/old', response_class=RedirectResponse)
async def startupold(
    request: Request,
):
    url = request.app.starting_url if hasattr(request.app, 'starting_url') else '/base'
    return RedirectResponse(url)
