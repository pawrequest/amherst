# from __future__ import annotations
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
from starlette.templating import Jinja2Templates
from suppawt.office_ps.email_handler import EmailError, Email
from suppawt.office_ps.ms.outlook_handler import emailer
from urllib3.exceptions import ConnectTimeoutError

from amherst.front.jin_book import book_shipment, subject, record_tracking
from shipaw import ELClient, Shipment, ship_types, BookingState
from amherst import am_db
from amherst.am_config import am_sett
from amherst.front import support
from shipaw.models import Contact
from shipaw.models.all_shipment_types import SHIPMENT_NOTES_FIELDNAMES, ShipmentRequest
from shipaw.models.pf_ext import AddressChoice, AddressCollection
from shipaw.models.pf_shared import ServiceCode
from shipaw.ship_types import VALID_POSTCODE

TEMPLATES = Jinja2Templates(directory=str(am_sett().base_dir / 'front' / 'templates'))

router = APIRouter()


@router.post('/print', response_class=HTMLResponse)
async def print_label(request: Request, label_path: str = Form(...)):
    """Endpoint to print the label for a booking."""
    pawdf.array_pdf.convert_many(Path(label_path), print_files=True)
    return HTMLResponse(content=f'<p>Printed {label_path}</p>')



@router.post('/email', response_class=HTMLResponse)
async def email(request: Request, shiprec_id: int = Form(...), session=Depends(am_db.get_session)):
    """Endpoint to handle email options."""
    shiprec = await support.get_shiprec(shiprec_id, session)
    form_data = await request.form()
    addresses = [value for key, value in form_data.items() if
                 value and key.startswith('email-')]
    addresses = '; '.join(addresses)

    att_choices = [key.lstrip('att-') for key, value in form_data.items() if
                   value and key.startswith('att-')]
    if invoice := 'invoice' in att_choices:
        invoice = shiprec.record.invoice.with_suffix('.pdf')
    if label := 'label' in att_choices:
        label = shiprec.booking_state.label_dl_path
    if missing := 'missing' in att_choices:
        missing = shiprec.record.missing_kit

    email_obj = await make_email(addresses, invoice, label, missing, shiprec.booking_state)

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


async def make_email(addresses, invoice, label, missing, booking_state):
    email_body = TEMPLATES.get_template('email.html').render(
        {
            'booking_state': booking_state,
            'invoice': invoice,
            'label': label,
            'missing': missing,
        }
    )
    subject_str = await subject(
        invoice.stem if invoice else None,
        missing is not False,
        label is not False
    )
    email_obj = Email(
        to_address=addresses,
        subject=subject_str,
        body=email_body,
        attachment_paths=[x for x in [label, invoice] if x],
    )
    return email_obj


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
        shiprec_id: int = Form(...),
        shipment_request: str = Form(...),
        el_client: ELClient = Depends(am_db.get_el_client),
        session: Session = Depends(am_db.get_session),
):
    shipment_request = ShipmentRequest.model_validate_json(shipment_request)
    booking_state: BookingState | None = None
    logger.warning(f'booking_id: {shiprec_id}')
    shiprec = await support.get_shiprec(shiprec_id, session)

    try:
        if hasattr(shiprec, 'booking_state') and shiprec.booking_state:
            logger.error(f'Shipment for {shiprec.record.name} already booked')
            return ValueError(f'Shipment for {shiprec.record.name} already booked')

        booking_state = book_shipment(el_client, shipment_request)
        record_tracking()

        label_path = shipment_request.label_path
        support.wait_label_decon(
            shipment_num=booking_state.response.shipment_num,
            dl_path=label_path,
            el_client=el_client
        )
        booking_state.label_downloaded = True
        booking_state.label_dl_path = label_path
        shiprec.booking_state = booking_state

        session.add(shiprec)
        session.commit()
        return TEMPLATES.TemplateResponse(
            'order_confirmed.html',
            {'request': request, 'booking_state': booking_state, 'shiprec': shiprec}
        )
    except Exception as e:
        if booking_state:
            return TEMPLATES.TemplateResponse(
                'order_confirmed.html',
                {'request': request, 'booking_state': booking_state, 'shiprec': shiprec}
            )

        return f'<p>ERROR: {str(e)}</p>'


async def get_notes_f_form(form_data):
    return [(fieldname, form_data[fieldname]) for fieldname in SHIPMENT_NOTES_FIELDNAMES if
            fieldname in form_data]


@router.post('/post_form/{shiprec_id}', response_class=HTMLResponse)
async def post_form(
        request: Request,
        shiprec_id: int,
        ship_date: date = Form(...),
        boxes: int = Form(...),
        direction: ship_types.ShipDirection = Form(...),
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
        # reference_number1: str = Form(''),
        # special_instructions1: str = Form(''),
        # reference_number2: str = Form(''),
        # special_instructions2: str = Form(''),
        # reference_number3: str = Form(''),
        # special_instructions3: str = Form(''),
        # reference_number4: str = Form(''),
        # special_instructions4: str = Form(''),
        pfcom: ELClient = Depends(am_db.get_el_client),
):
    try:
        address = AddressCollection(
            address_line1=address_line1,
            address_line2=address_line2,
            address_line3=address_line3,
            town=town,
            postcode=postcode,
        )
        contact = Contact(
            business_name=business_name,
            contact_name=contact_name,
            email_address=email,
            mobile_phone=phone,
        )
        shipment = Shipment(
            address=address,
            contact=contact,
            service=service,
            ship_date=ship_date,
            boxes=boxes,
            direction=direction,
        )
        for fieldname, value in await get_notes_f_form(await request.form()):
            setattr(shipment, fieldname, value)

        shipment = shipment.model_validate(shipment)

        return TEMPLATES.TemplateResponse(
            'review_order.html',
            {
                'request': request, 'shipment_request': shipment.shipment_request(),
                'shiprec_id': shiprec_id
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


@router.get('/{shiprec_id}', response_class=HTMLResponse)
async def index(
        request: Request,
        shiprec_id: int,
        session=Depends(am_db.get_session),
        el_client: ELClient = Depends(am_db.get_el_client),
):
    shiprec = await support.get_shiprec(shiprec_id, session)
    addr_choices = el_client.get_choices(
        shiprec.shipment.address.postcode,
        shiprec.shipment.address
    )
    return TEMPLATES.TemplateResponse(
        'base_form.html', {'request': request, 'shiprec': shiprec, 'candidates': addr_choices}
    )
