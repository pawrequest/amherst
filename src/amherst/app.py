import contextlib
import os
from pathlib import Path

import flaskwebgui
import pawdf
from fastapi import Depends, FastAPI, Query, responses
from fastapi.exceptions import RequestValidationError
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from amherst.back.backend_pycommence import pycmc_f_query, pycommence_response
from amherst.back.backend_search_paginate import SearchRequest, SearchResponse
from amherst.config import TEMPLATES, settings
from amherst.back.routes_json import router as json_router
from amherst.back.routes_ship import router as ship_router
from amherst.models.maps import listing_template_name_q
from pycommence.pycommence_v2 import PyCommence
from shipaw import pf_config


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
app.mount('/static', StaticFiles(directory=str(settings().src_dir / 'front' / 'static')), name='static')
app.include_router(json_router, prefix='/api')
app.include_router(ship_router, prefix='/ship')
app.ship_live = pf_config.pf_sett().ship_live


@app.exception_handler(RequestValidationError)
async def request_exception_handler(request: Request, exc: RequestValidationError):
    # req_data = await request.json()
    logger.error(f'Validation error at {request.url}: {exc.errors()}')
    # logger.error(f'Request data: {req_data}')
    return JSONResponse(status_code=422, content={'detail': exc.errors()})
    # return JSONResponse(status_code=422, content={'detail': exc.errors(), 'request_data': req_data})


@app.get('/open-file', response_class=HTMLResponse)
async def open_file(request: Request, filepath: str = Query(...)):
    os.startfile(filepath)
    return HTMLResponse(content=f'<p>Opened {filepath}</p>')


@app.post('/print-file', response_class=HTMLResponse)
async def print_file(request: Request, filepath: str = Query(...)):
    pawdf.array_pdf.convert_many(Path(filepath), print_files=True)
    return HTMLResponse(content=f'<p>Printed {filepath}</p>')


@app.get('/search')
async def search(
    request: Request,
    pycmc: PyCommence = Depends(pycmc_f_query),
    search_request: SearchRequest = Depends(SearchRequest.from_query),
    template_name: str = Depends(listing_template_name_q),
):
    search_response: SearchResponse = await pycommence_response(search_request, pycmc)
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': search_response})


# @app.get('/search', response_class=HTMLResponse)
# async def listing(
#     request: Request,
#     search_request: SearchRequest = Depends(SearchRequest.from_query2),
#     search_response: SearchResponse = Depends(pycommence_response),
#     template_name: str = Depends(listing_template_name_q),
# ):
#     return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': search_response})


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
    return responses.RedirectResponse(url='/static/favicon.svg')


@app.get('/api/health/', response_model=str)
async def health():
    return 'healthy'


@app.get('/testing/', response_model=str)
async def testing(
    request: Request,
):
    return TEMPLATES.TemplateResponse('testing.html', {'request': request})


@app.get('/', response_class=HTMLResponse)
async def base(
    request: Request,
):
    return TEMPLATES.TemplateResponse('base.html', {'request': request})
