import contextlib

from fastapi import FastAPI, responses
from fastapi.exceptions import RequestValidationError
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.staticfiles import StaticFiles

from amherst.back.routes_html import router as html_router
from amherst.back.routes_json import router as json_router
from amherst.back.ship_routes import router as ship_router
from amherst.config import amherst_settings
from shipaw.config import ShipawSettings
from shipaw.fapi.alerts import Alerts
from shipaw.fapi.app import request_validation_exception_handler
from shipaw.fapi.routes_html import router as shipaw_html_router
from shipaw.fapi.routes_api import router as shipaw_json_router


@contextlib.asynccontextmanager
async def lifespan(app_: FastAPI):
    try:
        # set_pf_env()
        # pythoncom.CoInitialize()
        # with sqm.Session(am_db.ENGINE) as session:
        #     pf_shipper = ELClient()
        #     populate_db_from_cmc(session, pf_shipper)
        yield

    finally:
        # pythoncom.CoUninitialize()

        ...


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory=str(ShipawSettings.from_env().static_dir)), name='static')
# app.mount('/static', StaticFiles(directory=str(amherst_settings().static_dir)), name='static')
app.include_router(json_router, prefix='/api')
app.include_router(ship_router, prefix='/shipaw')
app.include_router(shipaw_json_router, prefix='/shipaw/api')
app.include_router(shipaw_html_router, prefix='/shipaw')
app.include_router(html_router)
# app.ship_live = pf_config.pf_sett().ship_live
app.alerts = Alerts.empty()


@app.exception_handler(RequestValidationError)
async def request_exception_handler(request: Request, exc: RequestValidationError):
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
    return amherst_settings().templates.TemplateResponse('base.html', {'request': request})


@app.get('/', response_class=RedirectResponse)
async def startup(
    request: Request,
):
    url = request.app.starting_url if hasattr(request.app, 'starting_url') else '/base'
    return RedirectResponse(url)

