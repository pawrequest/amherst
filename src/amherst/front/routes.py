# from __future__ import annotations
import base64
import os
from datetime import date
from pathlib import Path

import pawdf
from combadge.core.errors import BackendError
from fastapi import APIRouter, Depends, Form
from loguru import logger
from sqlmodel import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from suppawt.office_ps.email_handler import EmailError
from suppawt.office_ps.ms.outlook_handler import emailer
from urllib3.exceptions import ConnectTimeoutError
from shipaw import ELClient, ship_types
from shipaw.models import Contact
from shipaw.models.pf_shipment import (ShipmentReferenceFields, ShipmentRequest)
from shipaw.models.pf_models import AddressChoice, AddressCollection, AddressRecipient
from shipaw.models.pf_shared import Alert, DateTimeRange, ServiceCode
from shipaw.models.pf_top import CollectionContact, CollectionInfo
from shipaw.pf_config import pf_sett
from shipaw.ship_types import VALID_POSTCODE

from amherst.front.backend_funcs import book_shipment, make_email, record_tracking
from amherst.front.support import TEMPLATES
from amherst.models.db_models import BookingStateDB
from amherst import am_db
from amherst.front import support

router = APIRouter()


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
async def email(request: Request, booking_id: int = Form(...), session=Depends(am_db.get_session)):
    """Endpoint to handle email options."""
    booking: BookingStateDB = await support.get_booking(booking_id, session)
    form_data = await request.form()
    addresses = [value for key, value in form_data.items() if
                 value and key.startswith('email-')]
    addresses = '; '.join(addresses)

    att_choices = [key.lstrip('att-') for key, value in form_data.items() if
                   value and key.startswith('att-')]
    if invoice := 'invoice' in att_choices:
        invoice = Path(booking.record.invoice_path).with_suffix('.pdf')
    if label := 'label' in att_choices:
        label = booking.label_path()
    if missing := 'missing' in att_choices:
        missing = booking.record.missing_kit()

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

    # logger.info(f'Email options received: {email_options}')

    # Process email options as needed
    # processed_options = ', '.join([f"{key}: {value}" for key, value in email_options.items()])


#
# @router.post('/email', response_class=HTMLResponse)
# async def email(request : Request, label_path: str = Form(...)):
#     """Endpoint to print the label for a booking."""
#     logger.info(f'printing')
#     array_pdf.convert_many(Path(label_path), print_files=True)
#     return HTMLResponse(content=f'<p>Printed {label_path}</p>')


@router.post("/confirm_booking", response_class=HTMLResponse)
async def confirm_booking(
        request: Request,
        booking_id: int = Form(...),
        el_client: ELClient = Depends(am_db.get_el_client),
        session: Session = Depends(am_db.get_session),
):
    logger.info(f'booking_id: {booking_id}')
    booking: BookingStateDB = await support.get_booking(booking_id, session)

    try:
        if booking.response:
            logger.error(f'Shipment for {booking.record.name} already booked')
            return TEMPLATES.TemplateResponse(
                'alerts.html',
                {'booking': booking, 'request': request}
            )

        booking.response = book_shipment(el_client, booking.shipment_request)
        booking.booked = True
        record_tracking(booking)

        label_dl_path = booking.label_path()
        support.wait_label(
            shipment_num=booking.response.shipment_num,
            dl_path=label_dl_path,
            el_client=el_client
        )
        booking.label_downloaded = True

        session.add(booking)
        session.commit()
        return TEMPLATES.TemplateResponse(
            'order_confirmed.html',
            {'request': request, 'booking': booking}
        )
    except Exception as e:
        alert = Alert.from_exception(e)
        booking.alerts.append(alert)
        if booking.response:
            session.add(booking)
            session.commit()
            return TEMPLATES.TemplateResponse(
                'order_confirmed.html',
                {
                    'request': request,
                    'booking': booking
                }
            )
        return TEMPLATES.TemplateResponse(
            'alerts.html',
            {'alert': alert, 'request': request, 'booking': booking}
        )


async def get_notes_f_form(form_data):
    return [(fieldname, form_data[fieldname]) for fieldname in
            ShipmentReferenceFields.model_fields.keys() if
            fieldname in form_data]


@router.post('/post_form/', response_class=HTMLResponse)
async def post_form(
        request: Request,
        booking_id: int = Form(...),
        ship_date: date = Form(...),
        boxes: int = Form(...),
        direction: ship_types.ShipDirectionEnum = Form(...),
        service: ServiceCode = Form(...),
        contact_name: str = Form(...),
        email: str = Form(...),
        business_name: str = Form(...),
        phone: str = Form(...),
        address_line1: str = Form(...),
        address_line2: str = Form(''),
        address_line3: str = Form(''),
        town: str = Form(...),
        postcode: VALID_POSTCODE = Form(...),
        session=Depends(am_db.get_session),
):
    try:
        addr_class = AddressRecipient if direction == 'out' else AddressCollection
        contact_class = Contact if direction == 'out' else CollectionContact
        address = addr_class(
            address_line1=address_line1,
            address_line2=address_line2,
            address_line3=address_line3,
            town=town,
            postcode=postcode,
        )
        contact = contact_class(
            business_name=business_name,
            contact_name=contact_name,
            email_address=email,
            mobile_phone=phone,
        )
        shipment_request = ShipmentRequest(
            recipient_address=address if direction == 'out' else pf_sett().home_address,
            recipient_contact=contact if direction == 'out' else pf_sett().home_contact,
            service_code=service,
            shipping_date=ship_date,
            total_number_of_parcels=boxes,
            collection_info=CollectionInfo(
                collection_contact=contact,
                collection_address=address,
                collection_time=DateTimeRange.null_times_from_date(ship_date),
            ) if direction == 'in' else None,
        )

        for fieldname, value in await get_notes_f_form(await request.form()):
            setattr(shipment_request, fieldname, value)

        booking = await support.get_booking(booking_id, session)
        booking.shipment_request = shipment_request
        session.add(booking)
        session.commit()

        return TEMPLATES.TemplateResponse(
            'order_review.html',
            {
                'request': request, 'booking': booking,
            },
        )
    except (ConnectTimeoutError, BackendError) as e:
        msg = f'Error: {e.__class__.__name__}. Connection Likely Timed Out.\n{str(e)}'
        logger.exception(msg)
        return f'<p>{msg}</p><p>Please refresh the page and try again</p>'
    except Exception as e:
        logger.error(e)
        return f'<p>{str(e)}</p><p>Please refresh the page and try again</p>'


@router.get('/get_candidates', response_class=JSONResponse)
async def get_candidates_json(  #
        postcode: VALID_POSTCODE,
        el_client: ELClient = Depends(am_db.get_el_client),
):
    res = el_client.candidates_json(postcode)
    return res


@router.get('/get_candidatesp', response_model=list[AddressChoice], response_class=JSONResponse)
async def get_candidatesp(
        postcode: VALID_POSTCODE,
        el_client: ELClient = Depends(am_db.get_el_client),
):
    res = el_client.get_choices(postcode)
    return res


@router.get('/{booking_id}', response_class=HTMLResponse)
async def index(
        request: Request,
        booking_id: int,
        session=Depends(am_db.get_session),
        el_client: ELClient = Depends(am_db.get_el_client),
):
    booking = await support.get_booking(booking_id, session)
    addr_choices = el_client.get_choices(
        booking.shipment_request.recipient_address.postcode,
        booking.shipment_request.recipient_address
    )
    return TEMPLATES.TemplateResponse(
        'input.html', {'request': request, 'booking': booking, 'candidates': addr_choices}
    )
