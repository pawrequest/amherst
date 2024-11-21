from __future__ import annotations

import json
import pathlib
import time
from datetime import date

from fastapi import Depends, Form
from loguru import logger
from pydantic import EmailStr, ValidationError
from starlette.requests import Request

from amherst.models.amherst_models import (
    AmherstShipment,
    AmherstShipmentAwayCollection,
    AmherstShipmentAwayDropoff,
    AmherstTableBase,
)
from amherst.config import TEMPLATES
from shipaw import ship_types
from shipaw.expresslink_client import ELClient
from shipaw.models import pf_msg, pf_shared
from shipaw.models.pf_models import AddressCollection, AddressRecipient, AddressSender
from shipaw.models.pf_msg import Alert, BaseResponse
from shipaw.models.pf_shared import ServiceCode
from shipaw.models.pf_shipment import Shipment, ShipmentReferenceFields
from shipaw.models.pf_top import CollectionInfo, Contact, ContactCollection, ContactSender
from shipaw.pf_config import pf_sett
from shipaw.ship_types import (
    AlertType,
    ExpressLinkError,
    ExpressLinkNotification,
    ExpressLinkWarning,
    ShipDirection,
    ShipmentType,
    VALID_POSTCODE,
)

from amherst.models.maps import maps2


def book_shipment(el_client, shipment: Shipment) -> pf_msg.ShipmentResponse:
    resp: pf_msg.ShipmentResponse = el_client.request_shipment(shipment)
    logger.debug(f'Booking response: {resp.status=}, {resp.success=}')
    if resp.alerts:
        adict = get_alert_dict(resp)
        logger.warning(f'Alerts: {adict}')

    return resp


def get_alert_dict(resp: BaseResponse) -> dict:
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
    contact_name: str = Form(...),
    email_address: EmailStr = Form(...),
    business_name: str = Form(...),
    mobile_phone: str = Form(...),
    direction: ship_types.ShipDirection = Form(...),
):
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


def to_amherst_dropoff(
    shipment: AmherstShipment, home_address=pf_sett().home_address, home_contact=pf_sett().home_contact
) -> AmherstShipmentAwayDropoff:
    try:
        return AmherstShipmentAwayDropoff.model_validate(
            shipment.model_copy(
                update={
                    'recipient_contact': home_contact,
                    'recipient_address': home_address,
                    'sender_contact': ContactSender(**shipment.recipient_contact.model_dump(exclude={'notifications'})),
                    'sender_address': AddressSender(**shipment.recipient_address.model_dump(exclude_none=True)),
                }
            ),
            from_attributes=True,
        )
    except ValidationError as e:
        logger.error(f'Error converting Shipment to Dropoff: {e}')
        raise


def to_amherst_collection(
    shipment: AmherstShipment, home_address=pf_sett().home_address, home_contact=pf_sett().home_contact, own_label=True
) -> AmherstShipmentAwayCollection:
    try:
        return AmherstShipmentAwayCollection.model_validate(
            shipment.model_copy(
                update={
                    'shipment_type': ShipmentType.COLLECTION,
                    'print_own_label': own_label,
                    'collection_info': CollectionInfo(
                        collection_address=AddressCollection(**shipment.recipient_address.model_dump()),
                        collection_contact=ContactCollection.model_validate(
                            shipment.recipient_contact.model_dump(exclude={'notifications'})
                        ),
                        collection_time=pf_shared.DateTimeRange.null_times_from_date(shipment.shipping_date),
                    ),
                    'recipient_contact': home_contact,
                    'recipient_address': home_address,
                }
            ),
            from_attributes=True,
        )
    except ValidationError as e:
        logger.error(f'Error converting Shipment to Collection: {e}')
        raise e


async def shipment_f_form2(
    contact: Contact = Depends(contact_f_form),
    address: AddressCollection = Depends(address_f_form),
    notes: list[tuple[str, str]] = Depends(notes_f_form),
    shipping_date: date = Form(...),
    total_number_of_parcels: int = Form(...),
    service_code: ServiceCode = Form(...),
    direction: ship_types.ShipDirection = Form(...),
    own_label: str = Form(...),
    row_id: str = Form(...),
    category: str = Form(...),
) -> Shipment:
    logger.warning('Creating Amherst Shipment Request from form')

    own_label = own_label.lower() == 'true'
    shipment_request = AmherstShipment(
        recipient_address=address,
        recipient_contact=contact,
        service_code=service_code,
        shipping_date=shipping_date,
        total_number_of_parcels=total_number_of_parcels,
        row_id=row_id,
        category=category,
    )
    if direction == ShipDirection.DROPOFF:
        shipment_request = to_amherst_dropoff(shipment_request)
    elif direction == ShipDirection.INBOUND:
        shipment_request = to_amherst_collection(shipment_request, own_label=own_label)

    for fieldname, value in notes:
        setattr(shipment_request, fieldname, value)
    return shipment_request


def get_el_client() -> ELClient:
    try:
        return ELClient()
    except Exception as e:
        logger.error(f'Error getting Parcelforce ExpressLink Client: {e}')
        raise


# async def shipment_from_record(record: AmherstTableBase, jsonable: bool = False) -> Shipment:
#     shipdict = record.shipment_dict()
#     shipment = Shipment(**shipdict)
#     shipment = shipment.model_validate(shipment)
#     logger.debug(f'Shipment request: {shipment}')
#     if jsonable:
#         shipment = jsonable_encoder(shipment)
#     return shipment


async def shipment_str_to_shipment(shipment_str: str = Form(...)):
    return Shipment.model_validate_json(shipment_str)


async def amherst_shipment_str_to_shipment(shipment_str: str = Form(...)):
    return AmherstShipment.model_validate_json(shipment_str)


async def record_str_to_record(record_str: str = Form(...)) -> AmherstTableBase:
    record_dict = json.loads(record_str)
    category = record_dict['category']
    rectype: AmherstTableBase = (await maps2(category)).record_model
    return rectype.model_validate_json(record_str)


async def check_dates(booking, request):
    alert = None
    if not booking.shipment_request.shipping_date.weekday() < 5:
        alert = Alert(type=AlertType.WARNING, message='Collection date must be a weekday')
    if booking.direction == ShipDirection.INBOUND and booking.shipment_request.shipping_date <= date.today():
        alert = Alert(type=AlertType.WARNING, message='Away Collections must be in the future')
    if alert:
        logger.warning(alert.message)
        booking.alerts.alert.append(alert)
        return TEMPLATES.TemplateResponse('alerts.html', {'booking': booking, 'request': request})
    return None
