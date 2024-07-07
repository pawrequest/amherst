# from __future__ import annotations
import base64
import os
from pathlib import Path

import pawdf
from fastapi import APIRouter, Depends, Form
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse

from amherst.config import TEMPLATES
from amherst.back.route_depends import (template_name_from_query, SearchRequest, SearchResponse)
from amherst.back.pyc_backend import pycommence_response

router = APIRouter()


@router.get('/test')
async def test(request: Request):
    logger.warning('TEST')
    return HTMLResponse(content='<h1>Test</h1>')


@router.get('/search')
async def search_get[T: SearchResponse](
        request: Request,
        search_request: SearchRequest = Depends(SearchRequest.from_query),
        template_name: str = Depends(template_name_from_query),
) -> HTMLResponse:
    response: T = await pycommence_response(search_request)
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})


@router.post('/search')
async def search_post[T: SearchResponse](
        request: Request,
        search_request: SearchRequest = Depends(SearchRequest.from_body),
        template_name: str = Depends(template_name_from_query),
) -> HTMLResponse:
    response: T = await pycommence_response(search_request)
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})


@router.get('/multi', response_class=HTMLResponse)
async def multi_shipper(
        request: Request,
):
    return TEMPLATES.TemplateResponse('multi.html', {'request': request})


@router.get('/fail/{alert}', response_class=HTMLResponse)
async def fail(request: Request, alert: str):
    alert = base64.urlsafe_b64decode(alert).decode('utf-8')
    logger.exception(f'Error: {alert}')
    return TEMPLATES.TemplateResponse('fail.html', {'request': request, 'alert': alert})


@router.post('/print', response_class=HTMLResponse)
async def print_label(request: Request, label_path: str = Form(...)):
    """Endpoint to print the label for a booking."""
    pawdf.array_pdf.convert_many(Path(label_path), print_files=True)
    return HTMLResponse(content=f'<p>Printed {label_path}</p>')


@router.post('/open-file', response_class=HTMLResponse)
async def open_label(request: Request, label_path: str = Form(...)):
    """Endpoint to print the label for a booking."""
    os.startfile(label_path)
    return HTMLResponse(content=f'<p>Opened {label_path}</p>')
