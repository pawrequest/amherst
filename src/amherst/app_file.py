import contextlib

import flaskwebgui
import pythoncom
from fastapi import FastAPI, responses
from fastui import prebuilt_html
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.staticfiles import StaticFiles

from amherst import am_config, front
from amherst.front.jinji import router as jinji_router
settings = am_config.AmSettings()
static_path = settings.base_dir / 'front' / 'static'


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

app.include_router(front.shipping_router, prefix='/api/ship')
app.include_router(front.booking_router, prefix='/api/book')
app.include_router(front.booked_router, prefix='/api/booked')
app.include_router(front.forms_router, prefix='/api/forms')
app.include_router(front.email_router, prefix='/api/email')
app.include_router(front.shared_router, prefix='/api/shared')
app.include_router(jinji_router, prefix='/jinji')


@app.get('/api/close_app/', response_model=None, response_model_exclude_none=True)
async def close_app(
):
    """Endpoint to close the application."""
    am_config.logger.warning('Closing application')
    flaskwebgui.close_application()


@app.get('/robots.txt', response_class=responses.PlainTextResponse)
async def robots_txt() -> str:
    return 'User-agent: *\nAllow: /'


# @app.get('/favicon.ico', status_code=404, response_class=responses.PlainTextResponse)
@app.get('/favicon.ico', include_in_schema=False)
async def favicon_ico() -> responses.RedirectResponse:
    return responses.RedirectResponse(url='/static/favicon.svg')


# def populate_db_from_cmc(session: sqm.Session, el_client):
#     records = sample_data.hires
#     # with cmc.csr_context(shipable_item.Hire.cmc_table_name) as csr:
#     #     filters = shipable_item.Hire.initial_filter_array.default
#     #     records = csr.filter_by_array(filters, get=True)
#     records = records[:3]
#     managers = rec_importer.hire_records_to_managers(*records, el_client=el_client)
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
# class LoggingMiddleware:
#     def __init__(self, app:Callable):
#         self.app = app
#
#     async def __call__(self, request: fastapi.Request, call_next: Callable) -> fastapi.Response:
#         response = await call_next(request)
#         logger.info(
#             f'Request: {request.method} {request.url} - Status code: {response.status_code}'
#         )
#         return response
#
#
# app.add_middleware(LoggingMiddleware)
#


#
# @app.middleware("http")
# async def add_process_time_header(request: fastapi.Request, call_next):
#     response = await call_next(request)
#     logger.info()
#     return response

#
# async def log_request_middleware(request: fastapi.Request, call_next: Callable) -> fastapi.Response:
#     """
#     Uniquely identify each request and logs its processing time.
#     """
#     start_time = time()
#     request_id: str = token_urlsafe(8)
#
#     # keep the same request_id in the context of all subsequent calls to logger
#     with logger.contextualize(request_id=request_id):
#         response = await call_next(request)
#         # final_time = time()
#         # elapsed = final_time - start_time
#
#         # response_dict = {
#         #     'status': response.status_code,
#         #     'headers': response.headers.raw,
#         # }
#         # atoms = AccessLogAtoms(request, response_dict, final_time)  # type: ignore
#         logger.info(
#             request.path_params.get('path'),
#         )
#     return response
#
#
# app.add_middleware(BaseHTTPMiddleware, dispatch=log_request_middleware)
#
#


# @app.middleware("http")
# async def co_initialize_middleware(request: Request, call_next):
#     try:
#         pythoncom.CoInitialize()
#         response = await call_next(request)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         pythoncom.CoUninitialize()
#     return response