from __future__ import annotations

from typing import Annotated

import fastapi
from fastui import FastUI, components as c, events as e
from fastui.forms import fastui_form
from loguru import logger

import shipr
import shipr.models.types
from amherst import am_db
from amherst.routers.booking_route import get_manager
from shipr.models.types import PostcodeSelect
from shipr.ship_ui.forms import AddressForm, ContactForm

router = fastapi.APIRouter()


@router.post('/postcode/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def postcode_post(
        manager_id: int,
        form: Annotated[PostcodeSelect, fastui_form(PostcodeSelect)],
):
    if not shipr.models.types.is_valid_postcode(form.postcode_to_fetch_addresses_from):
        logger.warning(f'Invalid postcode: {form.postcode_to_fetch_addresses_from}')
        return [c.FireEvent(event=e.GoToEvent(url=f'/hire/view/{manager_id}'))]
    return [
        c.FireEvent(
            event=e.GoToEvent(
                url=f'/hire/pcneighbours/{manager_id}/{form.postcode_to_fetch_addresses_from}'
            )
        )
    ]


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
            event=e.GoToEvent(
                url=f'/hire/update/{manager_id}/{man_in.state.update_dump_64(contact=contact)}'
            ),
        )
    ]


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
            event=e.GoToEvent(
                url=f'/hire/update/{manager_id}/{man_in.state.update_dump_64(address=address)}'
            ),
        )
    ]
