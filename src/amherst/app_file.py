import contextlib

import flaskwebgui
from fastapi import FastAPI, responses
from loguru import logger
from starlette.staticfiles import StaticFiles

from shipaw import pf_config
from amherst.front.routes import router
from amherst import am_config

settings = am_config.AmSettings()
static_path = settings.base_dir / 'front' / 'static'
pf_settings = pf_config.pf_sett()


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
app.mount('/static', StaticFiles(directory=str(static_path)), name='static')

app.include_router(router)
app.ship_live = pf_settings.ship_live


@app.get('/api/close_app/', response_model=None, response_model_exclude_none=True)
async def close_app(
):
    """Endpoint to close the application."""
    am_config.logger.warning('Closing application')
    flaskwebgui.close_application()


@app.get('/robots.txt', response_class=responses.PlainTextResponse)
async def robots_txt() -> str:
    return 'User-agent: *\nAllow: /'


@app.get('/favicon.ico', include_in_schema=False)
async def favicon_ico():
    logger.warning("Redirecting to /static/favicon.svg")
    return responses.RedirectResponse(url='/static/favicon.svg')
