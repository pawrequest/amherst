import contextlib
import pathlib

import fastapi
from starlette.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from amherst.front.jin_route import router as jin_router


@contextlib.asynccontextmanager
async def lifespan(app_: fastapi.FastAPI):
    try:
        # am_db.create_db()
        # with sqm.Session(am_db.ENGINE) as session:
        #     pf_shipper = shipper.AmShipper.from_env()
        #     populate_db_from_cmc(session, pf_shipper)

        # logger.info('tables created')
        yield

    finally:
        # am_db.destroy_db()
        ...
        # main_task.cancel()
        # await asyncio.gather(main_task)


BASE_DIR = pathlib.Path(__file__).resolve().parent

app = fastapi.FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory='/front/templates')
# app.mount("/front/static", StaticFiles(directory="/front/static"), name="static")
app.mount('/front/static', StaticFiles(directory=BASE_DIR / 'front/static'), name='static')
app.mount('/front/templates', StaticFiles(directory=BASE_DIR / 'front/templates'), name='templates')

app.include_router(jin_router, prefix='')


# app.include_router(rout, prefix="/api/rout")


@app.get('/robots.txt', response_class=fastapi.responses.PlainTextResponse)
async def robots_txt() -> str:
    return 'User-agent: *\nAllow: /'


@app.get('/favicon.ico', status_code=404, response_class=fastapi.responses.PlainTextResponse)
async def favicon_ico() -> str:
    return 'page not found'

# def populate_db_from_cmc(session: sqm.Session, pfcom):
#     records = sample_data.hires
#     # with cmc.csr_context(hire_model.Hire.cmc_table_name) as csr:
#     #     filters = hire_model.Hire.initial_filter_array.default
#     #     records = csr.filter_by_array(filters, get=True)
#     records = records[:3]
#     managers = rec_importer.hire_records_to_managers(*records, pfcom=pfcom)
#     session.add_all(managers)
#     session.commit()


# @app.get('/{path:path}')
# async def html_landing() -> fastapi.responses.HTMLResponse:
#     return fastapi.responses.HTMLResponse(fastui.prebuilt_html(title='Amherst'))
#

# @app.exception_handler(ManagerNotFound)
# async def manager_not_found_exception_handler(request: Request, exc: ManagerNotFound):
#     alert_dict: pawui_types.AlertDict = {'BOOKING NOT FOUND': 'ERROR'}
#     return await builders.page_w_alerts(alert_dict=alert_dict, components=[builders.back_link])
#