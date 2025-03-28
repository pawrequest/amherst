import contextlib
import os
from pathlib import Path

from fastapi import FastAPI, responses
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles



from amherst.config import TEMPLATES, settings
from amherst.back.routes_json import router as json_router
from amherst.back.routes_html import router as html_router
from amherst.back.routes_ship import router as ship_router2
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
app.mount('/static', StaticFiles(directory=str(settings().src_dir / 'front' / 'static')), name='static')
app.include_router(json_router, prefix='/api')
app.include_router(ship_router2, prefix='/ship')
app.include_router(html_router)
app.ship_live = pf_config.pf_sett().ship_live


@app.exception_handler(RequestValidationError)
async def request_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f'Validation error at {request.url}: {exc.errors()}')
    return JSONResponse(status_code=422, content={'detail': exc.errors()})


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
