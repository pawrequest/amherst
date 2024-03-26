from __future__ import annotations

import datetime as dt
from typing import Annotated

import fastapi
import pydantic as _p
from fastui import FastUI, components as c, events as e
from fastui.forms import fastui_form
from loguru import logger

import shipr
import shipr.types
from amherst import am_db, shipper
from amherst.routers.back_funcs import get_manager
from shipr.models import pf_ext, pf_top
from shipr.types import PostcodeSelect
from shipr.ship_ui import forms as ship_forms, states

router = fastapi.APIRouter()


# @router.post('/boxes/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
# async def boxes_post(
#         manager_id: int,
#         form: Annotated[BoxesModelForm, fastui_form(BoxesModelForm)],
# ):
#     ...
#     return [c.FireEvent(event=e.GoToEvent(url=f'/ship/view/{manager_id}'))]


@router.post('/postcode/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def postcode_post(
        manager_id: int,
        form: Annotated[PostcodeSelect, fastui_form(PostcodeSelect)],
) -> list[c.AnyComponent]:
    if not shipr.types.is_valid_postcode(form.fetch_address_from_postcode):
        logger.warning(f'Invalid postcode: {form.fetch_address_from_postcode}')
        return [c.FireEvent(event=e.GoToEvent(url=f'/ship/view/{manager_id}'))]
    return [
        c.FireEvent(
            event=e.GoToEvent(
                url=f'/sl/pcneighbours/{manager_id}/{form.fetch_address_from_postcode}'
            )
        )
    ]


class FormType(_p.BaseModel):
    boxes: int
    date: dt.date
    direction: str
    address: str


@router.post('/big/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def big_post(
        manager_id: int,
        date=fastapi.Form(...),
        boxes=fastapi.Form(...),
        direction=fastapi.Form(...),
        address=fastapi.Form(...),
        business_name=fastapi.Form(...),
        email=fastapi.Form(...),
        phone=fastapi.Form(...),
        service=fastapi.Form(...),
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),

):
    address = pf_ext.AddressRecipient.model_validate_json(address)
    contact = pf_top.Contact(
        business_name=business_name,
        email_address=email,
        mobile_phone=phone,
    )
    state = states.ShipState.model_validate(
        states.ShipState(
            boxes=boxes,
            ship_date=date,
            direction=direction,
            address=address,
            contact=contact,
            candidates=pfcom.get_candidates(address.postcode),
            service=service,

        )
    )
    return [c.FireEvent(
        event=e.GoToEvent(
            url=f'/ship/update/{manager_id}/{state.model_dump_64()}'

        )
    )
    ]


# @router.post('/contact/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
# async def contact_post(
#         manager_id: int,
#         form: Annotated[ContactForm, fastui_form(ContactForm)],
#         session=fastapi.Depends(am_db.get_session),
# ) -> list[c.AnyComponent]:
#     man_in = await get_manager(manager_id, session)
#     contact = shipr.models.Contact.model_validate(form.model_dump())
#     man_in.state.contact = contact
#     session.add(man_in)
#     session.commit()
#     return [
#         c.FireEvent(
#             event=e.GoToEvent(
#                 url=f'/ship/update/{manager_id}/{man_in.state.update_dump_64(contact=contact)}'
#             ),
#         )
#     ]

# class AddressForm(_p.BaseModel):
#     address: str


@router.post(
    '/address/{manager_id}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def address_post(
        manager_id: int,
        form: Annotated[ship_forms.AddressForm, fastui_form(ship_forms.AddressForm)],
):
    addy = pf_ext.AddressRecipient.model_validate(form.model_dump())
    return [
        c.FireEvent(
            event=e.GoToEvent(
                url=f'/ship/update/{manager_id}/{states.ShipStatePartial(address=addy).model_dump_64()}'
            )
        )
    ]


@router.post(
    '/boxes/{manager_id}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def boxes_post(
        manager_id: int,
        boxes: int = fastapi.Form(...),
):
    return [
        c.FireEvent(
            event=e.GoToEvent(
                url=f'/ship/update/{manager_id}/{states.ShipStatePartial(boxes=boxes).model_dump_64()}'
            ),
        )
    ]


@router.post(
    '/address_contact/{manager_id}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def address_contact_post(
        manager_id: int,
        form: Annotated[
            ship_forms.ContactAndAddressForm, fastui_form(ship_forms.ContactAndAddressForm)],
        session=fastapi.Depends(am_db.get_session),
):
    man_in = await get_manager(manager_id, session)
    contact = shipr.models.Contact(
        business_name=form.business_name,
        email_address=form.email_address,
        mobile_phone=form.mobile_phone,
        contact_name=form.contact_name,
    )
    address = shipr.models.AddressRecipient(
        address_line1=form.address_line1,
        address_line2=form.address_line2,
        address_line3=form.address_line3,
        town=form.town,
        postcode=form.postcode,
        country=form.country,
    )
    address = address.model_validate(address)
    contact = contact.model_validate(contact)
    return [
        c.FireEvent(
            event=e.GoToEvent(
                url=f'/ship/update/{manager_id}/{man_in.state.update_dump_64_dict(address=address, contact=contact)}'
            ),
        )
    ]

# @router.post(
#     '/big/{manager_id}',
#     response_model=FastUI,
#     response_model_exclude_none=True
# )
# async def big_post(
#         manager_id: int,
#         session=fastapi.Depends(am_db.get_session),
#         contact=fastapi.Form(...),
#         address=fastapi.Form(...),
#         boxes=fastapi.Form(...),
#         ship_date=fastapi.Form(...),
#         direction=fastapi.Form(...),
# ):
#     man_in = await get_manager(manager_id, session)
#     form_data = dict(
#         boxes=boxes,
#         ship_date=ship_date,
#         direction=direction.value,
#         contact=pf_top.Contact.model_validate(
#             contact
#         ),
#         address=pf_ext.AddressRecipient.model_validate(
#             address
#         ),
#
#     )
#
#     return [
#         c.FireEvent(
#             event=e.GoToEvent(
#                 url=f'/ship/update/{manager_id}/{man_in.state.update_dump_64_dict(update={**form_data})}'
#             ),
#         )
#     ]


# @router.post(
#     '/big1/{manager_id}',
#     response_model=FastUI,
#     response_model_exclude_none=True
# )
# async def big_post1(
#         manager_id: int,
#         form: Annotated[ship_forms.FullForm, fastui_form(ship_forms.FullForm)],
#         session=fastapi.Depends(am_db.get_session),
# ):
#     man_in = await get_manager(manager_id, session)
#     form_data = dict(
#         boxes=form.boxes,
#         ship_date=form.ship_date,
#         direction=form.direction.value,
#         contact=pf_top.Contact.model_validate(
#             shipr.models.Contact(
#                 business_name=form.business_name,
#                 email_address=form.email_address,
#                 mobile_phone=form.mobile_phone,
#                 contact_name=form.contact_name,
#             )
#         ),
#         address=pf_ext.AddressRecipient.model_validate(
#             shipr.models.AddressRecipient(
#                 address_line1=form.address_line1,
#                 address_line2=form.address_line2,
#                 address_line3=form.address_line3,
#                 town=form.town,
#                 postcode=form.postcode,
#                 country=form.country,
#             ),
#         ),
#
#     )
#
#     return [
#         c.FireEvent(
#             event=e.GoToEvent(
#                 url=f'/ship/update/{manager_id}/{man_in.state.update_dump_64_dict(update={**form_data})}'
#             ),
#         )
#     ]

# @router.post('/address/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
# async def address_post(
#         manager_id: int,
#         form: Annotated[AddressForm, fastui_form(AddressForm)],
#         session=fastapi.Depends(am_db.get_session),
# ) -> list[c.AnyComponent]:
#     man_in = await get_manager(manager_id, session)
#     address = shipr.models.AddressRecipient.model_validate(form.model_dump())
#     man_in.state.address = address
#     session.add(man_in)
#     session.commit()
#     return [
#         c.FireEvent(
#             event=e.GoToEvent(
#                 url=f'/ship/update/{manager_id}/{man_in.state.update_dump_64(address=address)}'
#             ),
#         )
#     ]
