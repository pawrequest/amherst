# from __future__ import annotations
import base64
import os
from pathlib import Path

import pawdf
from combadge.core.errors import BackendError
from fastapi import APIRouter, Depends, Form
from loguru import logger
from sqlmodel import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse
from urllib3.exceptions import ConnectTimeoutError

from amherst.backend_funcs import (
    TEMPLATES,
    new_amrec_f_path, shipment_request_f_form,
)
from amherst.db import get_session
from amherst.models.am_record_smpl import AmherstTableDB
from shipaw.models.pf_shipment import Shipment
from shipaw.ship_types import ShipDirection

router = APIRouter()


@router.get('/get_shipment/{row_id}', response_class=HTMLResponse)
async def fetch_amrec(
        request: Request,
        amrec: AmherstTableDB = Depends(new_amrec_f_path),
) -> HTMLResponse:
    return TEMPLATES.TemplateResponse('record_detail.html', {'request': request, 'record': amrec})


# @router.get('/getform/{row_id}', response_class=HTMLResponse)
# async def get_form_row_id(
#         request: Request,
#         amrec: AmherstTable = Depends(amgen_from_path),
#         el_client: ELClient = Depends(get_el_client_non_strict),
# ):
#     booking = amrec_to_booking(amrec)
#     addr_choices = el_client.get_choices(
#         booking.shipment_request.recipient_address.postcode, booking.shipment_request.recipient_address
#     )
#     logger.warning(f'address_choice = {booking.record.address_choice}')
#     return TEMPLATES.TemplateResponse(
#         'shipping_form.html', {'request': request, 'booking': booking, 'candidates': addr_choices}
#     )

@router.get('/multi', response_class=HTMLResponse)
async def multi_shipper(request: Request, session=Depends(get_session)):
    records = session.query(AmherstTableDB).all()
    return TEMPLATES.TemplateResponse('multi.html', {'request': request, 'records': records})


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

# @router.post('/email', response_class=HTMLResponse)
# async def email(request: Request, booking_id: int = Form(...), session=Depends(get_session)):
#     """Endpoint to handle email options."""
#     booking: BookingStateDB = await get_booking(booking_id, session)
#     form_data = await request.form()
#     # addresses = [value for key, value in form_data.items() if value and key.startswith('email-')]
#     addresses = form_data.getlist('email-options')
#     addresses = '; '.join(addresses)
# 
#     att_choices = [key.lstrip('att-') for key, value in form_data.items() if value and key.startswith('att-')]
#     if invoice := 'invoice' in att_choices:
#         logger.debug(f'fetching invoice path {booking.record.invoice_path}')
#         invoice = Path(booking.record.invoice_path).with_suffix('.pdf')
#     if label := 'label' in att_choices:
#         logger.debug(f'fetching label path {booking.label_path}')
#         label = booking.label_path
#     if missing := 'missing' in att_choices:
#         missing = booking.record.missing_kit()
#         logger.debug(f'fetching missing kit data {missing}')
# 
#     email_obj = await make_email(addresses, invoice, label, missing, booking)
# 
#     try:
#         emailer(email_obj, html=True)
#     except EmailError as e:
#         msg = 'Error sending email'
#         if '-2147221005' in e.args:
#             msg = f'{msg} - Outlook not open'
#             logger.exception(msg)
#         return HTMLResponse(content=f'<p>{msg} {e}</p>')
#     else:
#         return HTMLResponse(content='<p>Email created and opened</p>')


# @router.post('/confirm_booking', response_class=HTMLResponse)
# async def confirm_booking(
#         request: Request,
#         booking: BookingStateDB = Depends(booking_f_form),
#         el_client: ELClient = Depends(get_el_client),
#         session: Session = Depends(get_session),
# ):
#     logger.info(f'Booking {booking.id} for {booking.record.name}.')
# 
#     if booking.booked:
#         alert = Alert(type=AlertType.WARNING, message=f'Already Booked {booking.record.name}')
#         # booking.alerts.alert.append(alert)
#         # session.add(booking)
#         # session.commit()
#         # return TEMPLATES.TemplateResponse('alerts.html', {'booking': booking, 'request': request})
#         logger.debug(f'Already booked, alerts = {booking.alerts}')
#         return TEMPLATES.TemplateResponse('alerts_only.html', {'alerts': [alert], 'request': request})
# 
#     try:
#         booking.response = book_shipment(el_client, booking.shipment_request)
#         booking.booked = True
#         record_tracking(booking)
#         if (
#                 not isinstance(booking.shipment_request, ShipmentAwayCollection)
#                 or booking.shipment_request.print_own_label is not False
#         ):
#             await process_label(booking, el_client)
#         # if booking.shipment_request.print_own_label is not False:
#         #     await process_label(booking, el_client)
#         session.add(booking)
#         session.commit()
#         return TEMPLATES.TemplateResponse('order_confirmed.html', {'request': request, 'booking': booking})
# 
#     except (ConnectTimeoutError, BackendError) as e:
#         msg = f'Error: {e.__class__.__name__}. Connection Likely Timed Out.\n{str(e)}'
#         logger.exception(msg)
#         return f'<p>{msg}</p><p>Please refresh the page and try again</p>'
# 
#     except ExpressLinkError as e:
#         logger.exception(e)
#         al = Alert.from_exception(e)
#         logger.debug(f'ExpressLinkErro, alerts = {booking.alerts}')
#         booking.alerts.alert.append(al)
#         session.add(booking)
#         session.commit()
#         if booking.response:
#             return TEMPLATES.TemplateResponse('order_confirmed.html', {'request': request, 'booking': booking})
#         # return TEMPLATES.TemplateResponse('alerts.html', {'request': request, 'booking':booking})
#         return TEMPLATES.TemplateResponse('alerts_only.html', {'request': request, 'alerts': [al]})
# 
# 

#
# 
# @router.get('/{booking_id}', response_class=HTMLResponse)
# async def index(
#         request: Request,
#         booking: BookingStateDB = Depends(booking_f_path),
#         el_client: ELClient = Depends(get_el_client_non_strict),
# ):
#     addr_choices = el_client.get_choices(
#         booking.shipment_request.recipient_address.postcode, booking.shipment_request.recipient_address
#     )
#     logger.warning(f'address_choice = {booking.record.address_choice}')
#     return TEMPLATES.TemplateResponse(
#         'input.html', {'request': request, 'booking': booking, 'candidates': addr_choices}
#     )
