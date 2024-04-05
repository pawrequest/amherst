import contextlib

from fastapi import FastAPI, responses
from fastui import prebuilt_html

from amherst import am_db, front
from amherst.models import managers
from suppawt.pawlogger import get_loguru

logger = get_loguru(profile='local', log_file='amherst.log')


@contextlib.asynccontextmanager
async def lifespan(app_: FastAPI):
    try:
        # am_db.create_db()
        # am_db.delete_all_records(managers.BookingManagerDB)

        # with sqm.Session(am_db.ENGINE) as session:
        #     pf_shipper = shipper.AmShipper.from_env()
        #     populate_db_from_cmc(session, pf_shipper)

        # logger.info('tables created')
        yield

    finally:
        am_db.delete_all_records(managers.BookingManagerDB)
        ...


app = FastAPI(lifespan=lifespan)

app.include_router(front.shipping_router, prefix='/api/ship')
app.include_router(front.booking_router, prefix='/api/book')
app.include_router(front.booked_router, prefix='/api/booked')
app.include_router(front.forms_router, prefix='/api/forms')
app.include_router(front.ship_model_router, prefix='/api/ship_model')
app.include_router(front.forms_test_router, prefix='/api/forms_test')
app.include_router(front.splash_router, prefix='/api')


@app.get('/robots.txt', response_class=responses.PlainTextResponse)
async def robots_txt() -> str:
    return 'User-agent: *\nAllow: /'


@app.get('/favicon.ico', status_code=404, response_class=responses.PlainTextResponse)
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


@app.get('/{path:path}')
async def html_landing() -> responses.HTMLResponse:
    return responses.HTMLResponse(prebuilt_html(title='Amherst'))

#
# @app.exception_handler(
#     back_funcs.ManagerNotFound,
# )
# async def manager_not_found_exception_handler(
#         request: Request,
#         exc: back_funcs.ManagerNotFound
# ):
#     alert_dict: pawui_types.AlertDict = {'BOOKING NOT FOUND': 'ERROR'}
#     # return await builders.page_w_alerts(
#     #     alert_dict=alert_dict,
#     #     components=[builders.back_link(), c.Text(text='error')]
#     # )
#     return HTTPException(
#         status_code=404,
#         detail='Booking not found',
#     )
#
