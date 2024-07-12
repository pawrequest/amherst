import contextlib

import flaskwebgui
from fastapi import FastAPI, responses
from loguru import logger
from starlette.staticfiles import StaticFiles

from amherst.config import settings
from amherst.back.routes import router as html_router
from amherst.back.routes_api import router as json_router
from amherst.back.routes_ship import router as ship_router


@contextlib.asynccontextmanager
async def lifespan(app_: FastAPI):
    try:
        # pythoncom.CoInitialize()
        # with sqm.Session(am_db.ENGINE) as session:
        #     pf_shipper = ELClient()
        #     populate_db_from_cmc(session, pf_shipper)
        yield

    finally:
        # pythoncom.CoUninitialize()

        ...


app = FastAPI(lifespan=lifespan)
app.mount('/static', StaticFiles(directory=str(settings().base_dir / 'front' / 'static')), name='static')

app.include_router(html_router)
app.include_router(json_router, prefix='/api')
app.include_router(ship_router, prefix='/ship')
# app.ship_live = pf_config.pf_sett().ship_live


@app.get('/api/close_app/', response_model=None, response_model_exclude_none=True)
async def close_app():
    """Endpoint to close the application."""
    logger.warning('Closing application')
    flaskwebgui.close_application()


@app.get('/robots.txt', response_class=responses.PlainTextResponse)
async def robots_txt() -> str:
    return 'User-agent: *\nAllow: /'


@app.get('/favicon.ico', include_in_schema=False)
async def favicon_ico():
    logger.warning('Redirecting to /static/favicon.svg')
    return responses.RedirectResponse(url='/static/favicon.svg')


@app.get('/api/health/', response_model=str)
async def health():
    return 'healthy'
