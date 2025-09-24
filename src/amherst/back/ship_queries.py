from __future__ import annotations

import json
from datetime import date

from fastapi import Depends, Form
from loguru import logger
from pydantic import EmailStr

from amherst.models.amherst_models import AmherstShipableBase
from amherst.models.maps import mapper_from_query_csrname

from shipaw.agnostic.address import Address, Contact, FullContact
from shipaw.config import shipaw_settings
from shipaw.agnostic.providers import ShippingProvider
from shipaw.agnostic.requests import ShipmentRequestAgnost
from shipaw.agnostic.services import ServiceType
from shipaw.agnostic.ship_types import ShipDirection, VALID_POSTCODE
from shipaw.agnostic.shipment import Shipment

from shipaw.apc.provider import APCProvider
from shipaw.parcelforce.provider import ParcelforceProvider


async def get_provider(provider: str = Form(...)) -> type[ShippingProvider]:
    match provider:
        case 'PARCELFORCE':
            return ParcelforceProvider
        case 'APC':
            return APCProvider
        case _:
            raise ValueError(f'Unknown provider: {provider}')


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
    service: ServiceType = Form(...),
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


async def shipment_req_str_to_shipment(shipment_req_str: str = Form(...)) -> ShipmentRequestAgnost:
    ship_json = json.loads(shipment_req_str)
    shipy = ShipmentRequestAgnost.model_validate(ship_json)
    return shipy


async def shipment_req_str_to_shipment2(shipment_req_str: str = Form(...)) -> ShipmentRequestAgnost:
    ship_json = json.loads(shipment_req_str)
    shipy = ShipmentRequestAgnost.model_validate(ship_json)
    return shipy


async def record_str_to_record(record_str: str = Form(...)) -> AmherstShipableBase:
    record_dict = json.loads(record_str)
    mapper = await mapper_from_query_csrname(record_dict['row_info'][0])
    record = mapper.record_model.model_validate(record_dict)
    return record


# async def full_contact_from_form(
#     address_line1: str = Form(...),
#     address_line2: str = Form(''),
#     address_line3: str = Form(''),
#     town: str = Form(...),
#     postcode: VALID_POSTCODE = Form(...),
#     contact_name: str = Form(...),
#     email_address: EmailStr = Form(...),
#     business_name: str = Form(...),
#     mobile_phone: str = Form(...),
#     direction: ShipDirection = Form(...),
# ) -> FullContact:
#     logger.debug(
#         f'Address fields received: {direction=}, {address_line1=}, {address_line2=}, {address_line3=}, {town=}, {postcode=}'
#     )
#     return FullContact(
#         address=Address(
#             address_lines=[address_line1, address_line2, address_line3],
#             town=town,
#             postcode=postcode,
#         ),
#         contact=Contact(
#             business_name=business_name,
#             contact_name=contact_name,
#             email_address=email_address,
#             mobile_phone=mobile_phone,
#         ),
#     )


# async def shipment_f_form(
#     # full_contact: FullContact = Depends(full_contact_from_form),
#     full_contact2: FullContact = Depends(full_contact_from_form),
#     shipping_date: date = Form(...),
#     boxes: int = Form(...),
#     service: ServiceType = Form(...),
#     direction: ShipDirection = Form(...),
#     reference: str = Form('DIDNT PLUG IN REFERENCES!!!'),
# ) -> Shipment:
#     logger.info('Creating Amherst Shipment Request from form')
#
#     match direction:
#         case ShipDirection.OUTBOUND:
#             recipient = full_contact2
#             sender = None
#         case ShipDirection.INBOUND:
#             recipient = shipaw_settings().full_contact
#             sender = full_contact2
#         case _:
#             raise NotImplementedError('Dropoff not implemented')
#
#     shipment = Shipment(
#         recipient=recipient,
#         sender=sender,
#         boxes=boxes,
#         shipping_date=shipping_date,
#         direction=direction,
#         reference=reference,
#         service=service,
#     )
#     return shipment
