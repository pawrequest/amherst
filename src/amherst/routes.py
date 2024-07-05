# from __future__ import annotations
import base64
import os
from pathlib import Path

import pawdf
from fastapi import APIRouter, Depends, Form
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse

from amherst.backend_funcs import (
    TEMPLATES,
)
from amherst.db import get_rows_contain_pk, get_session
from amherst.route_depends import amrecs_and_more, template_name_from_path
from amherst.models.am_record_smpl import AMHERST_TABLE_TYPES, AmherstCustomerDB, AmherstHireDB, AmherstSaleDB
from amherst.multi_shipper import fresh_cmc_data
from amherst.routes_api import TABLE_LIST_More

router = APIRouter()


@router.get('/search_cmc/{csrname}/{pk_value}', response_class=HTMLResponse)
async def search_cmc(
        rows: list[dict] = Depends(get_rows_contain_pk),
        template_name: str = Depends(template_name_from_path)
) -> list[dict]:
    resolved = list(rows)
    return TEMPLATES.TemplateResponse(template_name, {'data': resolved})


@router.get('/search/{csrname}', response_class=HTMLResponse)
async def search(
        request: Request,
        recs_and_more: TABLE_LIST_More = Depends(amrecs_and_more),
        template_name: str = Depends(template_name_from_path),
) -> list[AMHERST_TABLE_TYPES]:
    records, more = recs_and_more
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'data': records})


@router.get('/multi', response_class=HTMLResponse)
async def multi_shipper(
        request: Request,
        session=Depends(get_session)
):
    await fresh_cmc_data()
    customers = session.query(AmherstCustomerDB).all()
    hires = session.query(AmherstHireDB).all()
    sales = session.query(AmherstSaleDB).all()
    orders = hires + sales

    return TEMPLATES.TemplateResponse('multi.html', {'request': request, 'customers': customers, 'orders': orders})


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
