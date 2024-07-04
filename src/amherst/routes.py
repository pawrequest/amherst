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
from amherst.db import get_session, get_them, template_name_from_path
from amherst.models.am_record_smpl import AMHERST_TABLE_TYPES, AmherstCustomerDB, AmherstHireDB, AmherstSaleDB
from amherst.multi_shipper import fresh_cmc_data
from amherst.routes_api import TABLE_LIST_More

router = APIRouter()


@router.get('/search/{category}', response_class=HTMLResponse)
async def search(
        request: Request,
        res: TABLE_LIST_More = Depends(get_them),
        template_name: str = Depends(template_name_from_path),
) -> list[AMHERST_TABLE_TYPES]:
    page, more = res
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'data': page})


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
