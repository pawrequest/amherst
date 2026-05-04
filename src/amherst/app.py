from fastapi import responses
from fastapi.exceptions import RequestValidationError
from loguru import logger
from pawlogger import configure_loguru
from shipaw.config import ShipawSettings, populate_providers, FapiConfig
from shipaw.fapi.app import request_validation_exception_handler
from shipaw.fapi.routes_api import router as shipaw_json_router
from shipaw.fapi.routes_html import router as shipaw_html_router
from shipaw.fapi.routes_html import shipping_form
from shipaw.models.shipment import Shipment
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles

from amherst.app_custom import AmherstApp, AmherstRequest, AppState
from amherst.callbacks import cmc_callback
from amherst.config import AMHERST_SETTINGS, AmherstSettings


def create_app(amherst_settings: AmherstSettings, shipaw_settings: ShipawSettings):
    app_ = AmherstApp()

    # state
    app_.state = AppState.create()
    app_.state.callback = cmc_callback

    # routing
    app_.mount('/static', StaticFiles(directory=str(shipaw_settings.static_dir)), name='static')
    app_.include_router(shipaw_json_router, prefix='/api')
    app_.include_router(shipaw_html_router)

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
    fapi_config: FapiConfig = request.app.state.config
    shipment = Shipment(**fapi_config.post_body)
    shipment.context = request.app.state.config.context
    res = await shipping_form(request, shipment=shipment)
    return res
