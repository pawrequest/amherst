from __future__ import annotations

import pathlib
import time
from datetime import date

from fastapi import Form, Depends
from loguru import logger
from pydantic import EmailStr

from amherst.models.amherst_models import AmherstTableBase
from shipaw.pf_config import PFSettings, pf_sett
from starlette.requests import Request

from amherst.config import TEMPLATES
from shipaw import ship_types
from shipaw.expresslink_client import ELClient
from shipaw.models import pf_msg
from shipaw.models.pf_models import AddressCollection, AddressRecipient
from shipaw.models.pf_msg import Alert
from shipaw.models.pf_shared import ServiceCode
from shipaw.models.pf_shipment import to_dropoff, to_collection, ShipmentConfigured
from shipaw.models.pf_shipment_blank import ShipmentReferenceFields
from shipaw.models.pf_top import Contact, ContactCollection
from shipaw.ship_types import (
    ExpressLinkError,
    ExpressLinkWarning,
    ExpressLinkNotification,
    VALID_POSTCODE,
    ShipDirection,
    AlertType,
)


def book_shipment(el_client, shipment_request: ShipmentConfigured) -> pf_msg.ShipmentResponse:
    resp: pf_msg.ShipmentResponse = el_client.request_shipment(shipment_request)
    logger.debug(f'Booking response: {resp.status=}, {resp.success=}')
    if resp.alerts:
        adict = get_alert_dict(resp)
        logger.warning(f'Alerts: {adict}')

    if resp.completed_shipment_info:
        if completed_list := resp.completed_shipment_info.completed_shipments.completed_shipment:
            logger.info(rf'Shipment/s booked: {[_.shipment_number for _ in completed_list]}')
        else:
            logger.warning('No shipment booked')

    return resp


def get_alert_dict(resp):
    a_dict = {}
    for a in resp.alerts.alert:
        try:
            a.raise_exception()
        except ExpressLinkWarning as warned:
            a_dict['warning'] = warned
        except ExpressLinkNotification as noted:
            a_dict['note'] = noted
        except ExpressLinkError as error:
            a_dict['error'] = error
    return a_dict


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
    logger.debug(f'{addr_class.__name__} Address validated: {addr}')
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
    logger.debug(f'{contact_class.__name__} Contact validated: {cont}')
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
) -> ShipmentConfigured:
    logger.warning('Creating Shipment Request from form')
    own_label = own_label.lower() == 'true'
    shipment_request = ShipmentConfigured(
        recipient_address=address,
        recipient_contact=contact,
        service_code=service_code,
        shipping_date=shipping_date,
        total_number_of_parcels=total_number_of_parcels,
    )
    if direction == ShipDirection.Dropoff:
        shipment_request = to_dropoff(shipment_request)
        # shipment_request = ShipmentAwayDropoff.from_shipment(shipment_request)
    elif direction == ShipDirection.Inbound:
        shipment_request = to_collection(shipment_request, own_label=own_label)

    for fieldname, value in notes:
        setattr(shipment_request, fieldname, value)

    return shipment_request


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


def get_el_client() -> ELClient:
    try:
        return ELClient()
    except Exception as e:
        logger.error(f'Error getting Parcelforce ExpressLink Client: {e}')
        raise


# def get_pf_settings() -> PFSettings:
#     try:
#         return pf_sett()
#     except Exception as e:
#         logger.error(f'Error getting Parcelforce Settings: {e}')
#         raise

async def shipment_from_row(row: AmherstTableBase) -> ShipmentConfigured:
    shipdict = row.shipment_dict()
    shipment = ShipmentConfigured(**shipdict)
    shipment = shipment.model_validate(shipment)
    logger.debug(f'Shipment request: {shipment}')
    return shipment
