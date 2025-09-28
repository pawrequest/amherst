from __future__ import annotations

import json
from datetime import date

from fastapi import Depends, Form
from loguru import logger
from pydantic import EmailStr

from amherst.models.amherst_models import AmherstShipableBase
from amherst.models.maps import mapper_from_query_csrname
from shipaw.models.address import Address, Contact, FullContact
from shipaw.config import shipaw_settings
from shipaw.fapi.requests import ShipmentRequest as ShipmentRequest
from shipaw.models.ship_types import ShipDirection, VALID_POSTCODE
from shipaw.models.shipment import Shipment


async def full_contact_from_form(
    address_line1: str = Form(...),
    address_line2: str = Form(''),
    address_line3: str = Form(''),
    town: str = Form(...),
    postcode: VALID_POSTCODE = Form(...),
    contact_name: str = Form(...),
    email_address: EmailStr = Form(...),
    business_name: str = Form(...),
    mobile_phone: str = Form(...),
    direction: ShipDirection = Form(...),
) -> FullContact:
    logger.debug(
        f'Address fields received: {direction=}, {address_line1=}, {address_line2=}, {address_line3=}, {town=}, {postcode=}'
    )
    return FullContact(
        address=Address(
            address_lines=[address_line1, address_line2, address_line3],
            town=town,
            postcode=postcode,
            business_name=business_name,
        ),
        contact=Contact(
            contact_name=contact_name,
            email_address=email_address,
            mobile_phone=mobile_phone,
        ),
    )


async def shipment_f_form(
    full_contact: FullContact = Depends(full_contact_from_form),
    shipping_date: date = Form(...),
    boxes: int = Form(...),
    service: str = Form(...),
    direction: ShipDirection = Form(...),
    reference: str = Form('DIDNT PLUG IN REFERENCES!!!'),
) -> Shipment:
    logger.info('Creating Amherst Shipment Request from form')

    if direction == ShipDirection.OUTBOUND:
        recipient = full_contact
        sender = None
    elif direction in {ShipDirection.INBOUND, ShipDirection.DROPOFF}:
        recipient = shipaw_settings().full_contact
        sender = full_contact
    else:
        raise ValueError(f'Unknown direction: {direction}')

    shipment = Shipment(
        recipient=recipient,
        sender=sender,
        boxes=boxes,
        shipping_date=shipping_date,
        direction=direction,
        reference=reference,
        service=service,
    )
    return shipment


async def shipment_str_to_shipment(shipment_str: str = Form(...)) -> Shipment:
    ship_json = json.loads(shipment_str)
    shipy = Shipment.model_validate(ship_json)
    return shipy


async def shipment_req_str_to_shipment(shipment_req_str: str = Form(...)) -> ShipmentRequest:
    ship_json = json.loads(shipment_req_str)
    shipy = ShipmentRequest.model_validate(ship_json)
    return shipy


async def shipment_req_str_to_shipment2(shipment_req_str: str = Form(...)) -> ShipmentRequest:
    ship_json = json.loads(shipment_req_str)
    shipy = ShipmentRequest.model_validate(ship_json)
    return shipy


async def record_str_to_record(record_str: str = Form(...)) -> AmherstShipableBase:
    record_dict = json.loads(record_str)
    mapper = await mapper_from_query_csrname(record_dict['row_info'][0])
    record = mapper.record_model.model_validate(record_dict)
    return record

