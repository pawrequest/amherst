import contextlib

from fastapi import FastAPI, responses
from fastapi.exceptions import RequestValidationError
from loguru import logger
from shipaw.models.pf_msg import Alert, Alerts
from shipaw.ship_types import AlertType
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.staticfiles import StaticFiles


from amherst.config import AM_SETTINGS, TEMPLATES
from amherst.back.routes_json import router as json_router
from amherst.back.routes_html import router as html_router
from amherst.back.ship_routes import router as ship_router2
from shipaw import pf_config


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
app.mount('/static', StaticFiles(directory=str(AM_SETTINGS.src_dir / 'front' / 'static')), name='static')
app.include_router(json_router, prefix='/api')
app.include_router(ship_router2, prefix='/ship')
app.include_router(html_router)
app.ship_live = pf_config.pf_sett().ship_live
app.alerts = Alerts.empty()


@app.exception_handler(RequestValidationError)
async def request_exception_handler(request: Request, exc: RequestValidationError):
    msg = f'Validation error at {request.url}: {exc.errors()}'
    errors = exc.errors()
    msg2 = ''
    for err in errors:
        msg2 += f'{err.get('type')} in {err.get('loc')}: {err.get('ctx').get('reason')}. Input = {err.get('input')} '

    logger.error(msg2)
    alerts = Alerts(alert=[Alert(code=1, message=msg2, type=AlertType.ERROR), RESTART])
    return TEMPLATES.TemplateResponse('alerts.html', {'request': request, 'alerts': alerts})

    # return JSONResponse(status_code=422, content={'detail': exc.errors()})


@app.get('/robots.txt', response_class=responses.PlainTextResponse)
async def robots_txt() -> str:
    return 'User-agent: *\nAllow: /'


@app.get('/favicon.ico', include_in_schema=False)
async def favicon_ico():
    return responses.RedirectResponse(url='/static/favicon.svg')


@app.get('/', response_class=HTMLResponse)
async def base(
    request: Request,
):
    return TEMPLATES.TemplateResponse('base.html', {'request': request})
