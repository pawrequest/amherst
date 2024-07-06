# from __future__ import annotations
import base64
import os
from pathlib import Path

import pawdf
from fastapi import APIRouter, Depends, Form
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse

from amherst.actions.emailer import TEMPLATES
from amherst.back.route_depends import (SearchResponse, search_body, search_query, template_name_from_path)

router = APIRouter()


@router.get('/search')
async def search_query[T: SearchResponse](
        request: Request,
        response: T = Depends(search_query),
        template_name: str = Depends(template_name_from_path),
) -> HTMLResponse:
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})


@router.post('/search')
async def search_post[T: SearchResponse](
        request: Request,
        response: T = Depends(search_body),
        template_name: str = Depends(template_name_from_path),
) -> HTMLResponse:
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})


# @router.post('/search')
# async def search_post[T: AMHERST_TABLE_TYPES](
#         request: Request,
#         records: list[T] = Depends(search_body),
#         template_name: str = Depends(template_name_from_body),
#         pagination: Pagination = Depends(Pagination.from_query),
# ) -> HTMLResponse:
#     for amrec in records:
#         logger.info(f'{amrec.name=} {type(amrec)=}')
#     return await get_template(template_name, records, request, pagination)


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
