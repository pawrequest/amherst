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
    new_amrec_f_path,
)
from amherst.db import amrecs_from_query, amrecs_from_query2, get_session
from amherst.models.am_record_smpl import AMHERST_TABLE_TYPES, AmherstCustomerDB, AmherstHireDB, AmherstSaleDB
from amherst.multi_shipper import fresh_cmc_data

router = APIRouter()


@router.get('/search2/{category}', response_class=HTMLResponse)
async def search2(request: Request, page: list[AMHERST_TABLE_TYPES] = Depends(amrecs_from_query2)):
    return TEMPLATES.TemplateResponse('customers.html', {'request': request, 'data': page})


@router.get('/search', response_class=HTMLResponse)
async def search(request: Request, page: list[AMHERST_TABLE_TYPES] = Depends(amrecs_from_query)):
    return TEMPLATES.TemplateResponse('records.html', {'request': request, 'records': page})


@router.get('/get_shipment/{row_id}', response_class=HTMLResponse)
async def fetch_amrec(
        request: Request,
        amrec: AMHERST_TABLE_TYPES = Depends(new_amrec_f_path),
) -> HTMLResponse:
    return TEMPLATES.TemplateResponse('record_detail.html', {'request': request, 'record': amrec})


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
