import contextlib
import sys

import fastapi
import sqlmodel as sqm
from dotenv import load_dotenv
from loguru import logger

import fastuipr
from amherst import am_db, rec_importer, routers, sample_data, shipper

load_dotenv()


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    try:
        am_db.create_db()
        with sqm.Session(am_db.ENGINE) as session:
            pfcom = shipper.AmShipper.from_env()
        # populate_db_from_cmc(session, pfcom)

        logger.info('tables created')
        # main_task = asyncio.create_task()
        yield

    finally:
        ...
        # main_task.cancel()
        # await asyncio.gather(main_task)

app = fastapi.FastAPI(lifespan=lifespan)

app.include_router(routers.hire_router, prefix='/api/hire')
app.include_router(routers.booking_router, prefix='/api/book')
app.include_router(routers.forms_router, prefix='/api/forms')


# app.include_router(rout, prefix="/api/rout")


@app.get('/robots.txt', response_class=fastapi.responses.PlainTextResponse)
async def robots_txt() -> str:
    return 'User-agent: *\nAllow: /'


@app.get('/favicon.ico', status_code=404, response_class=fastapi.responses.PlainTextResponse)
async def favicon_ico() -> str:
    return 'page not found'


def populate_db_from_cmc(session: sqm.Session, pfcom):
    records = sample_data.hires
    # with cmc.csr_context(hire_model.Hire.cmc_table_name) as csr:
    #     filters = hire_model.Hire.initial_filter_array.default
    #     records = csr.filter_by_array(filters, get=True)
    records = records[:3]
    rec_importer.records_to_managers(session, pfcom, *records)


@app.get('/{path:path}')
async def html_landing() -> fastapi.responses.HTMLResponse:
    return fastapi.responses.HTMLResponse(fastuipr.prebuilt_html(title='Amherst'))
