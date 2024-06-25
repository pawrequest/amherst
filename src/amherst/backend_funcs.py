from __future__ import annotations

import pathlib
import time
import typing as _t
from datetime import date

from fastapi import Depends, Form, Path
from loguru import logger
from pydantic import BaseModel, EmailStr
from sqlmodel import Session
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from suppawt.office_ps.email_handler import Email

from amherst.commence import HireFields
from amherst.config import settings
from amherst.db import get_session
from amherst.models.am_record import AmherstRecord
from amherst.models.db_models import BookingStateDB
from pycommence import PyCommence
from shipaw import ship_types
from shipaw.expresslink_client import ELClient
from shipaw.models import pf_msg
from shipaw.models.pf_models import AddressCollection, AddressRecipient
from shipaw.models.pf_msg import Alert
from shipaw.models.pf_shared import ServiceCode
from shipaw.models.pf_shipment import (
    AnyShipment,
    Shipment,
    ShipmentAwayCollection,
    ShipmentAwayDropoff,
    ShipmentReferenceFields,
)
from shipaw.models.pf_top import Contact, ContactCollection
from shipaw.ship_types import AlertType, ExpressLinkNotification, ExpressLinkWarning, ShipDirection, VALID_POSTCODE

type EmailChoices = _t.Literal['invoice', 'label', 'missing_kit']


def book_shipment(el_client, shipment_request: AnyShipment) -> pf_msg.ShipmentResponse:
    resp: pf_msg.ShipmentResponse = el_client.request_shipment(shipment_request)
    for a in resp.alerts.alert if resp.alerts else []:
        try:
            a.raise_exception()
        except ExpressLinkWarning as warned:
            raise NotImplementedError(warned)
        except ExpressLinkNotification as noted:
            raise NotImplementedError(noted)
        if completed_list := resp.completed_shipment_info.completed_shipments.completed_shipment:
            logger.info(rf'Shipment/s booked: {[_.shipment_number for _ in completed_list]}')
    return resp


def record_tracking(booking_state: BookingStateDB):
    record = booking_state.record
    try:
        category = record.category
        if category == 'Customer':
            logger.error('CANT LOG TO CUSTOMER')
            return
        do_record_tracking(booking_state)
        logger.debug(f'Logged tracking for {category} {record.name}')

    except Exception as exce:
        logger.exception(exce)
        raise


def do_record_tracking(booking: BookingStateDB):
    tracking_link = booking.response.tracking_link()
    cmc_package = (
        {
            HireFields.TRACK_INBOUND: tracking_link,
            HireFields.ARRANGED_INBOUND: True,
            HireFields.PICKUP_DATE: f'{booking.shipment_request.shipping_date:%Y-%m-%d}',
        }
        if booking.direction in ['in', 'dropoff']
        else {HireFields.TRACK_OUTBOUND: tracking_link, HireFields.ARRANGED_OUTBOUND: True}
    )

    with PyCommence.from_table_name_context(table_name=booking.record.category) as py_cmc:
        py_cmc.edit_record(booking.record.name, row_dict=cmc_package)
    booking.tracking_logged = True
    logger.debug(f'Logged {str(cmc_package)} to Commence')


async def subject(invoice_num: str | None = None, missing=None, label=None):
    return (
        f'Amherst Radios'
        f'{f"- Invoice {invoice_num} Attached" if invoice_num else ""} '
        f'{"- We Are Missing Kit" if missing else ""} '
        f'{"- Shipping Label Attached" if label else ""}'
    )


async def make_email(addresses, invoice, label, missing, booking_state):
    email_body = TEMPLATES.get_template('email_body.html').render(
        {
            'booking_state': booking_state,
            'invoice': invoice,
            'label': label,
            'missing': missing,
        }
    )
    subject_str = await subject(invoice.stem if invoice else None, missing is not False, label is not False)
    email_obj = Email(
        to_address=addresses,
        subject=subject_str,
        body=email_body,
        attachment_paths=[x for x in [label, invoice] if x],
    )
    return email_obj


TEMPLATES = Jinja2Templates(directory=str(settings().base_dir / 'front' / 'templates'))


async def get_booking(booking_id: int, session: Session) -> BookingStateDB:
    record = session.get(BookingStateDB, booking_id)
    if not isinstance(record, BookingStateDB):
        raise ValueError(f'No booking found with id {booking_id}')
    return record


async def booking_f_form(booking_id: int = Form(), session: Session = Depends(get_session)) -> BookingStateDB:
    logger.debug(f'Retrieving Booking {booking_id} from form')
    booking = session.get(BookingStateDB, booking_id)
    if not isinstance(booking, BookingStateDB):
        raise ValueError(f'No booking found with id {booking_id}')
    return booking


async def booking_f_path(booking_id: int = Path(), session: Session = Depends(get_session)) -> BookingStateDB:
    booking = session.get(BookingStateDB, booking_id)
    if not isinstance(booking, BookingStateDB):
        raise ValueError(f'No booking found with id {booking_id}')
    return booking


def wait_label(shipment_num, dl_path: str, el_client: ELClient) -> pathlib.Path:
    label_path = el_client.get_label(ship_num=shipment_num, dl_path=dl_path).resolve()
    for i in range(20):
        if label_path:
            return label_path
        else:
            print('waiting for file to be created')
            time.sleep(1)
    else:
        raise ValueError(f'file not created after 20 seconds {label_path=}')


async def get_invoice_path(record: AmherstRecord) -> pathlib.Path | None:
    if record.category == 'Customer':
        raise ValueError('invoice not for customer')
    return record.invoice_path


async def get_missing(record: AmherstRecord) -> list[str]:
    if not record.category == 'Hire':
        raise ValueError('missing kit only for hire')
    return record.missing_kit()


async def address_f_form(
    address_line1: str = Form(...),
    address_line2: str = Form(''),
    address_line3: str = Form(''),
    town: str = Form(...),
    postcode: VALID_POSTCODE = Form(...),
    direction: ShipDirection = Form(...),
):
    logger.debug(
        f'Address fields received: {direction=}, {address_line1=}, {address_line2=}, {address_line3=}, {town=}, {postcode=}'
    )
    addr_class = AddressCollection if direction == 'in' else AddressRecipient
    addr = addr_class(
        address_line1=address_line1,
        address_line2=address_line2,
        address_line3=address_line3,
        town=town,
        postcode=postcode,
    )
    addr = addr.model_validate(addr)
    logger.debug(f'Address validated: {addr}')
    return addr


async def contact_f_form(
    request: Request,
    contact_name: str = Form(...),
    email_address: EmailStr = Form(...),
    business_name: str = Form(...),
    mobile_phone: str = Form(...),
    direction: ship_types.ShipDirection = Form(...),
):
    logger.debug(f'form received: {await request.form()}')
    logger.debug(
        f'Contact fields received: direction={direction}, {contact_name=}, {email_address=}, {business_name=}, {mobile_phone=}'
    )
    contact_class = Contact if direction == 'out' else ContactCollection
    cont = contact_class(
        business_name=business_name,
        contact_name=contact_name,
        email_address=email_address,
        mobile_phone=mobile_phone,
    )
    cont = cont.model_validate(cont)
    logger.debug(f'Contact validated: {cont}')
    return cont


async def notes_f_form(request: Request) -> list[tuple[str, str]]:
    logger.debug('Parsing notes from form')
    form_data = await request.form()
    notes = [
        (fieldname, form_data[fieldname])
        for fieldname in ShipmentReferenceFields.model_fields.keys()
        if fieldname in form_data
    ]
    return notes


async def shipment_request_f_form(
    request: Request,
    contact: Contact = Depends(contact_f_form),
    address: AddressCollection = Depends(address_f_form),
    notes: list[tuple[str, str]] = Depends(notes_f_form),
    shipping_date: date = Form(...),
    total_number_of_parcels: int = Form(...),
    service_code: ServiceCode = Form(...),
    direction: ship_types.ShipDirection = Form(...),
    own_label: str = Form(...),
) -> AnyShipment:
    logger.warning('Creating Shipment Request from form')
    own_label = own_label.lower() == 'true'
    shipment_request = Shipment(
        recipient_address=address,
        recipient_contact=contact,
        service_code=service_code,
        shipping_date=shipping_date,
        total_number_of_parcels=total_number_of_parcels,
    )
    if direction == ShipDirection.Dropoff:
        shipment_request = ShipmentAwayDropoff.from_shipment(shipment_request)
    elif direction == ShipDirection.Inbound:
        shipment_request = ShipmentAwayCollection.from_shipment(shipment_request, own_label=own_label)

    for fieldname, value in notes:
        setattr(shipment_request, fieldname, value)

    return shipment_request


async def process_label(booking: BookingStateDB, el_client):
    label_path = booking.get_label_path()
    wait_label(shipment_num=booking.response.shipment_num, dl_path=label_path, el_client=el_client)
    booking.label_downloaded = True
    booking.label_path = str(label_path)


async def check_dates(booking, request):
    alert = None
    if not booking.shipment_request.shipping_date.weekday() < 5:
        alert = Alert(type=AlertType.WARNING, message='Collection date must be a weekday')
    if booking.direction == ShipDirection.Inbound and booking.shipment_request.shipping_date <= date.today():
        alert = Alert(type=AlertType.WARNING, message='Away Collections must be in the future')
    if alert:
        logger.warning(alert.message)
        booking.alerts.alert.append(alert)
        return TEMPLATES.TemplateResponse('alerts.html', {'booking': booking, 'request': request})
    return None


async def _from_req_json(request: Request, model_type: type[BaseModel]):
    form_data = await request.json()
    form_data = form_data.get('data')
    c_data = {k: v for k, v in form_data.items() if k in model_type.model_fields}
    logger.warning(form_data)
    res = model_type.model_validate(c_data)
    return res
