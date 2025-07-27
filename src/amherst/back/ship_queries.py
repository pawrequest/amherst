from __future__ import annotations

import json
from datetime import date

from fastapi import Form, Depends
from loguru import logger
from pydantic import EmailStr
from shipaw import ship_types
from shipaw.models.pf_models import AddressCollection, AddressRecipient
from shipaw.models.pf_shared import ServiceCode
from shipaw.models.pf_shipment import ShipmentReferenceFields, Shipment, ShipmentAwayCollection, ShipmentAwayDropoff
from shipaw.models.pf_top import Contact, ContactCollection
from shipaw.ship_types import VALID_POSTCODE, ShipDirection, get_ship_direction
from starlette.requests import Request

from amherst.models.amherst_models import AmherstShipableBase
from amherst.models.maps import mapper_from_query_csrname


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
    logger.debug(f'{contact_class.__name__} validated: {cont}')
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


async def shipment_f_form(
    contact: Contact = Depends(contact_f_form),
    address: AddressCollection = Depends(address_f_form),
    notes: list[tuple[str, str]] = Depends(notes_f_form),
    shipping_date: date = Form(...),
    total_number_of_parcels: int = Form(...),
    service_code: ServiceCode = Form(...),
    direction: ship_types.ShipDirection = Form(...),
    own_label: str = Form(...),
) -> Shipment:
    logger.info('Creating Amherst Shipment Request from form')

    own_label = own_label.lower() == 'true'
    shipment = Shipment(
        recipient_address=address,
        recipient_contact=contact,
        service_code=service_code,
        shipping_date=shipping_date,
        total_number_of_parcels=total_number_of_parcels,
    )
    if direction == ShipDirection.DROPOFF:
        shipment = shipment.to_dropoff()

    elif direction == ShipDirection.INBOUND:
        shipment = shipment.to_collection(own_label=own_label)

    for fieldname, value in notes:
        setattr(shipment, fieldname, value)
    return shipment


async def shipment_str_to_shipment(shipment_str: str = Form(...)) -> Shipment:
    ship_json = json.loads(shipment_str)
    shipy = Shipment.model_validate(ship_json)
    ship_dir = get_ship_direction(ship_json)
    match ship_dir:
        case ShipDirection.OUTBOUND:
            return shipy
        case ShipDirection.INBOUND:
            return ShipmentAwayCollection.model_validate(shipy, from_attributes=True)
        case ShipDirection.DROPOFF:
            return ShipmentAwayDropoff.model_validate(shipy, from_attributes=True)
        case _:
            raise ValueError(f'Invalid shipment direction: {ship_dir}')


async def record_str_to_record(record_str: str = Form(...)) -> AmherstShipableBase:
    record_dict = json.loads(record_str)
    mapper = await mapper_from_query_csrname(record_dict['category'])
    record = mapper.record_model.model_validate(record_dict)
    return record
