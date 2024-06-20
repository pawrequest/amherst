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
from suppawt.office_ps.email_handler import EmailError
from suppawt.office_ps.ms.outlook_handler import emailer
from urllib3.exceptions import ConnectTimeoutError

from amherst.backend_funcs import (
    TEMPLATES,
    book_shipment,
    booking_f_form,
    booking_f_path,
    check_dates,
    get_booking,
    make_email,
    process_label,
    record_tracking,
    shipment_request_f_form,
)
from amherst.db import get_el_client, get_session
from amherst.models.db_models import BookingStateDB
from shipaw import ship_types
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_msg import Alert
from shipaw.models.pf_shipment import ShipmentRequest
from shipaw.ship_types import AlertType, ExpressLinkError

router = APIRouter()


@router.get('/multi', response_class=HTMLResponse)
async def multi_shipper(request: Request, session=Depends(get_session)):
    bookings = session.query(BookingStateDB).all()
    return TEMPLATES.TemplateResponse('multi.html', {'request': request, 'bookings': bookings})


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


@router.post('/email', response_class=HTMLResponse)
async def email(request: Request, booking_id: int = Form(...), session=Depends(get_session)):
    """Endpoint to handle email options."""
    booking: BookingStateDB = await get_booking(booking_id, session)
    form_data = await request.form()
    # addresses = [value for key, value in form_data.items() if value and key.startswith('email-')]
    addresses = form_data.getlist('email-options')
    addresses = '; '.join(addresses)

    att_choices = [key.lstrip('att-') for key, value in form_data.items() if value and key.startswith('att-')]
    if invoice := 'invoice' in att_choices:
        logger.debug(f'fetching invoice path {booking.record.invoice_path}')
        invoice = Path(booking.record.invoice_path).with_suffix('.pdf')
    if label := 'label' in att_choices:
        logger.debug(f'fetching label path {booking.label_path}')
        label = booking.label_path
    if missing := 'missing' in att_choices:
        missing = booking.record.missing_kit()
        logger.debug(f'fetching missing kit data {missing}')

    email_obj = await make_email(addresses, invoice, label, missing, booking)

    try:
        emailer(email_obj, html=True)
    except EmailError as e:
        msg = 'Error sending email'
        if '-2147221005' in e.args:
            msg = f'{msg} - Outlook not open'
            logger.exception(msg)
        return HTMLResponse(content=f'<p>{msg} {e}</p>')
    else:
        return HTMLResponse(content='<p>Email created and opened</p>')


@router.post('/confirm_booking', response_class=HTMLResponse)
async def confirm_booking(
    request: Request,
    booking: BookingStateDB = Depends(booking_f_form),
    el_client: ELClient = Depends(get_el_client),
    session: Session = Depends(get_session),
):
    logger.info(f'Booking {booking.id} for {booking.record.name}.')

    try:
        if booking.booked:
            alert = Alert(type=AlertType.WARNING, message=f'Already Booked {booking.record.name}')
            # booking.alerts.alert.append(alert)
            # session.add(booking)
            # session.commit()
            # return TEMPLATES.TemplateResponse('alerts.html', {'booking': booking, 'request': request})
            logger.debug(f'Already booked, alerts = {booking.alerts}')
            return TEMPLATES.TemplateResponse('alerts_only.html', {'alerts': [alert], 'request': request})

        booking.response = book_shipment(el_client, booking.shipment_request)
        booking.booked = True
        record_tracking(booking)
        if booking.shipment_request.print_own_label is not False:
            await process_label(booking, el_client)
        session.add(booking)
        session.commit()
        return TEMPLATES.TemplateResponse('order_confirmed.html', {'request': request, 'booking': booking})

    except (ConnectTimeoutError, BackendError) as e:
        msg = f'Error: {e.__class__.__name__}. Connection Likely Timed Out.\n{str(e)}'
        logger.exception(msg)
        return f'<p>{msg}</p><p>Please refresh the page and try again</p>'

    except ExpressLinkError as e:
        logger.exception(e)
        al = Alert.from_exception(e)
        logger.debug(f'ExpressLinkErro, alerts = {booking.alerts}')
        booking.alerts.alert.append(al)
        session.add(booking)
        session.commit()
        if booking.response:
            return TEMPLATES.TemplateResponse('order_confirmed.html', {'request': request, 'booking': booking})
        # return TEMPLATES.TemplateResponse('alerts.html', {'request': request, 'booking':booking})
        return TEMPLATES.TemplateResponse('alerts_only.html', {'request': request, 'alerts': [al]})


@router.post('/post_form/', response_class=HTMLResponse)
async def post_form(
    request: Request,
    direction: ship_types.ShipDirection = Form(...),
    booking: BookingStateDB = Depends(booking_f_form),
    shipment_request: ShipmentRequest = Depends(shipment_request_f_form),
    session: Session = Depends(get_session),
):
    try:
        booking.direction = direction
        booking.shipment_request = shipment_request
        session.add(booking)
        session.commit()

        if failed := await check_dates(booking, request):
            return failed

        return TEMPLATES.TemplateResponse(
            'order_review.html',
            {
                'request': request,
                'booking': booking,
            },
        )
    except (ConnectTimeoutError, BackendError) as e:
        msg = f'Error: {e.__class__.__name__}. Connection Likely Timed Out.\n{str(e)}'
        logger.exception(msg)
        return f'<p>{msg}</p><p>Please refresh the page and try again</p>'
    except Exception as e:
        logger.error(e)
        return f'<p>{str(e)}</p><p>Please refresh the page and try again</p>'


@router.get('/{booking_id}', response_class=HTMLResponse)
async def index(
    request: Request,
    booking: BookingStateDB = Depends(booking_f_path),
    el_client: ELClient = Depends(get_el_client),
):
    addr_choices = el_client.get_choices(
        booking.shipment_request.recipient_address.postcode, booking.shipment_request.recipient_address
    )
    logger.warning(f'address_choice = {booking.record.address_choice}')
    return TEMPLATES.TemplateResponse(
        'input.html', {'request': request, 'booking': booking, 'candidates': addr_choices}
    )


#
#
# @router.get('/{booking_id}', response_class=HTMLResponse)
# async def index(
#         request: Request,
#         booking_id: int,
#         session=Depends(get_session),
#         el_client: ELClient = Depends(get_el_client),
# ):
#     booking = await get_booking(booking_id, session)
#     addr_choices = el_client.get_choices(
#         booking.shipment_request.recipient_address.postcode, booking.shipment_request.recipient_address
#     )
#     return TEMPLATES.TemplateResponse(
#         'input.html', {'request': request, 'booking': booking, 'candidates': addr_choices}
#     )

#
# @router.post('/post_form/', response_class=HTMLResponse)
# async def post_form(
#     request: Request,
#     booking: BookingStateDB = Depends(booking_f_path),
#     shipping_date: date = Form(...),
#     boxes: int = Form(...),
#     direction: ship_types.ShipDirection = Form(...),
#     service: ServiceCode = Form(...),
#     own_label: bool = Form(...),
#     contact_name: str = Form(...),
#     email_address: EmailStr = Form(...),
#     business_name: str = Form(...),
#     mobile_phone: str = Form(...),
#     address_line1: str = Form(...),
#     address_line2: str = Form(''),
#     address_line3: str = Form(''),
#     town: str = Form(...),
#     postcode: VALID_POSTCODE = Form(...),
#     session=Depends(get_session),
# ):
#     try:
#         addr_class = AddressCollection if direction == 'in' else AddressRecipient
#         address = addr_class(
#             address_line1=address_line1,
#             address_line2=address_line2,
#             address_line3=address_line3,
#             town=town,
#             postcode=postcode,
#         )
#         contact_class = Contact if direction == 'out' else CollectionContact
#         contact = contact_class(
#             business_name=business_name,
#             contact_name=contact_name,
#             email_address=email_address,
#             mobile_phone=mobile_phone,
#         )
#         shipment_request = ShipmentRequest(
#             recipient_address=address,
#             recipient_contact=contact,
#             service_code=service,
#             shipping_date=shipping_date,
#             total_number_of_parcels=boxes,
#         )
#
#         for fieldname, value in await get_notes_f_form(await request.form()):
#             setattr(shipment_request, fieldname, value)
#
#         if direction == ShipDirection.Dropoff:
#             shipment_request.make_inbound()
#         elif direction == ShipDirection.Inbound:
#             shipment_request.make_collection(own_label=own_label)
#
#         booking.direction = direction
#         booking.shipment_request = shipment_request
#         session.add(booking)
#         session.commit()
#
#         if failed := await check_dates(booking, request):
#             return failed
#
#         return TEMPLATES.TemplateResponse(
#             'order_review.html',
#             {
#                 'request': request,
#                 'booking': booking,
#             },
#         )
#     except (ConnectTimeoutError, BackendError) as e:
#         msg = f'Error: {e.__class__.__name__}. Connection Likely Timed Out.\n{str(e)}'
#         logger.exception(msg)
#         return f'<p>{msg}</p><p>Please refresh the page and try again</p>'
#     except Exception as e:
#         logger.error(e)
#         return f'<p>{str(e)}</p><p>Please refresh the page and try again</p>'
#
