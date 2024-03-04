from __future__ import annotations

import typing as _t
from typing import Annotated

import fastapi
import pydantic
import pydantic as _p
from loguru import logger

import shipr
from amherst import am_db
from amherst.routers.booking_route import get_manager
from fastuipr import FastUI
from fastuipr import components as c
from fastuipr import events as e
from fastuipr.forms import fastui_form
from pawsupport.pydantic import pyd_types
from pawsupport.pydantic.pyd_types import default_gen, is_valid_postcode
from shipr import models as s_mod

router = fastapi.APIRouter()


class PostcodeSelect(_p.BaseModel):
    postcode_to_fetch_addresses_from: VALID_PC

    @classmethod
    def with_default(cls, postcode: str):
        dflt2 = default_gen(VALID_PC, default=postcode)

        class _PostcodeSelect(cls):
            postcode_to_fetch_addresses_from: dflt2

        return _PostcodeSelect


@router.post('/postcode/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def postcode_post(
    manager_id: int,
    form: Annotated[PostcodeSelect, fastui_form(PostcodeSelect)],
):
    if not is_valid_postcode(form.postcode_to_fetch_addresses_from):
        logger.warning(f'Invalid postcode: {form.postcode_to_fetch_addresses_from}')
        return [c.FireEvent(event=e.GoToEvent(url=f'/hire/view/{manager_id}'))]
    return [
        c.FireEvent(event=e.GoToEvent(url=f'/hire/pcneighbours/{manager_id}/{form.postcode_to_fetch_addresses_from}'))
    ]


class ContactForm(pydantic.BaseModel):
    business_name: pyd_types.TruncatedSafeStr(40)
    email_address: pyd_types.TruncatedSafeStr(50)
    mobile_phone: str
    contact_name: pyd_types.TruncatedSafeMaybeStr(30)

    @classmethod
    def with_default(cls, contact: s_mod.Contact):
        bus_t = default_gen(pyd_types.TruncatedSafeStr(40), default=contact.business_name)
        em_ = default_gen(pyd_types.TruncatedSafeStr(50), default=contact.email_address)
        mob_t = default_gen(str, default=contact.mobile_phone)
        con_t = default_gen(pyd_types.TruncatedSafeMaybeStr(30), default=contact.contact_name)

        class _ContactSelect(cls):
            business_name: bus_t
            email_address: em_
            mobile_phone: mob_t
            contact_name: con_t

        return _ContactSelect


@router.post('/contact/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def contact_post(
    manager_id: int,
    form: Annotated[ContactForm, fastui_form(ContactForm)],
    session=fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    man_in = await get_manager(manager_id, session)
    contact = shipr.models.Contact.model_validate(form.model_dump())
    man_in.state.contact = contact
    session.add(man_in)
    session.commit()
    return [
        c.FireEvent(
            event=e.GoToEvent(url=f'/hire/update/{manager_id}/{man_in.state.update_dump_64(contact=contact)}'),
        )
    ]


class AddressForm(pydantic.BaseModel):
    address_line1: pyd_types.TruncatedSafeStr(40)
    address_line2: pyd_types.TruncatedSafeMaybeStr(50)
    address_line3: pyd_types.TruncatedSafeMaybeStr(60)
    town: pyd_types.TruncatedSafeStr(30)
    postcode: str
    country: str = 'GB'

    @classmethod
    def with_default(cls, address: s_mod.AddressRecipient):
        add1_t = default_gen(pyd_types.TruncatedSafeStr(40), default=address.address_line1)
        add2_t = default_gen(pyd_types.TruncatedSafeMaybeStr(50), default=address.address_line2)
        add3_t = default_gen(pyd_types.TruncatedSafeMaybeStr(60), default=address.address_line3)
        town_t = default_gen(pyd_types.TruncatedSafeStr(30), default=address.town)
        post_t = default_gen(str, default=address.postcode)
        country_t = default_gen(str, default=address.country)

        class _AddressSelect(cls):
            address_line1: add1_t
            address_line2: add2_t
            address_line3: add3_t
            town: town_t
            postcode: post_t
            country: country_t

        return _AddressSelect


@router.post('/address/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def address_post(
    manager_id: int,
    form: Annotated[AddressForm, fastui_form(AddressForm)],
    session=fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    man_in = await get_manager(manager_id, session)
    address = shipr.models.AddressRecipient.model_validate(form.model_dump())
    man_in.state.address = address
    session.add(man_in)
    session.commit()
    return [
        c.FireEvent(
            event=e.GoToEvent(url=f'/hire/update/{manager_id}/{man_in.state.update_dump_64(address=address)}'),
        )
    ]


POSTCODE_PATTERN = r'([A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2})'
VALID_PC = _t.Annotated[
    str,
    _p.StringConstraints(pattern=POSTCODE_PATTERN),
    _p.BeforeValidator(lambda s: s.strip().upper()),
    _p.Field(..., description='A valid UK postcode'),
]
