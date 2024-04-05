from __future__ import annotations

import json
from typing import Annotated

import fastapi
from fastui import FastUI, components as c, events as e
from fastui.forms import fastui_form
from loguru import logger

import shipr
import shipr.shipr_types
from amherst import am_db, shipper
from amherst.front import support, ship
from amherst.models import managers
from pawdantic.pawui import pawui_types
from shipr import shipr_types
from shipr.models import pf_ext, pf_top
from shipr.ship_ui import forms as ship_forms, states

router = fastapi.APIRouter()


@router.post('/manual/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def manual_post(
        manager_id: int,

        date=fastapi.Form(...),
        boxes=fastapi.Form(...),
        direction=fastapi.Form(...),
        business_name=fastapi.Form(...),
        contact_name=fastapi.Form(...),
        email=fastapi.Form(...),
        phone=fastapi.Form(...),
        service=fastapi.Form(...),

        reference=fastapi.Form(''),
        special_instructions=fastapi.Form(''),

        address_line1=fastapi.Form(...),
        address_line2=fastapi.Form(''),
        address_line3=fastapi.Form(''),
        town=fastapi.Form(...),
        postcode=fastapi.Form(...),
        # country=fastapi.Form('GB'),
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),

):
    address_choice = pf_ext.AddressRecipient.model_validate(
        pf_ext.AddressRecipient(
            address_line1=address_line1,
            address_line2=address_line2,
            address_line3=address_line3,
            town=town,
            postcode=postcode,
            country='GB',

        )
    )

    contact = pf_top.Contact(
        business_name=business_name,
        contact_name=contact_name,

        email_address=email,
        mobile_phone=phone,
    )

    state = states.ShipState.model_validate(
        states.ShipState(
            reference=reference,
            special_instructions=special_instructions,
            boxes=boxes,
            ship_date=date,
            direction=direction,
            address=address_choice,
            contact=contact,
            candidates=pfcom.get_candidates(address_choice.postcode),
            service=service,

        )
    )
    return [c.FireEvent(
        event=e.GoToEvent(
            url=f'/book/confirm/{manager_id}/{state.model_dump_64()}'

        )
    )
    ]


@router.post('/select/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def select_post(
        manager_id: int,
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),

        address=fastapi.Form(None),

        reference=fastapi.Form(''),
        special_instructions=fastapi.Form(''),

        date=fastapi.Form(...),
        boxes=fastapi.Form(...),
        direction=fastapi.Form(...),
        business_name=fastapi.Form(...),
        contact_name=fastapi.Form(...),
        email=fastapi.Form(...),
        phone=fastapi.Form(...),
        service=fastapi.Form(...),

):
    address_choice = pf_ext.AddressRecipient.model_validate_json(address)

    contact = pf_top.Contact(
        business_name=business_name,
        contact_name=contact_name,
        email_address=email,
        mobile_phone=phone,
    )

    state = states.ShipState.model_validate(
        states.ShipState(
            boxes=boxes,
            ship_date=date,
            direction=direction,
            address=address_choice,
            contact=contact,
            candidates=pfcom.get_candidates(address_choice.postcode),
            service=service,
            reference=reference,
            special_instructions=special_instructions,

        )
    )
    return [c.FireEvent(
        event=e.GoToEvent(
            url=f'/book/confirm/{manager_id}/{state.model_dump_64()}'

        )
    )
    ]


@router.post(
    '/address/{manager_id}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def address_model_post(
        manager_id: int,
        form: Annotated[ship_forms.AddressForm, fastui_form(ship_forms.AddressForm)],
):
    addy = pf_ext.AddressRecipient.model_validate(form.model_dump())
    partial = states.ShipStatePartial(address=addy)
    return [
        c.FireEvent(
            event=e.GoToEvent(
                url=f'/ship/update/{manager_id}/{partial.model_dump_64()}'
            )
        )
    ]


@router.post(
    '/state/{manager_id}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def state_model_post(
        manager_id: int,
        form: Annotated[states.ShipStatePartial, fastui_form(states.ShipStatePartial)],
        session=fastapi.Depends(am_db.get_session),
):
    man_in = await support.get_manager(manager_id, session)
    man_in.state = shipr.ShipState.model_validate(
        man_in.state.get_updated(form)
    )

    session.add(man_in)
    session.commit()
    # return await shipping_page.ship_page(manager=man_in)

    return [
        c.FireEvent(
            event=e.GoToEvent(
                url=f'/ship/view/{manager_id}'
            )
        )
    ]


@router.post(
    '/address_form/{manager_id}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def address_form_post(
        request: fastapi.Request,
        manager_id: int,
        session=fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    form = await request.form()
    address_ = json.loads(form.get('address'))
    address = pf_ext.AddressRecipient.model_validate(address_)

    partial = states.ShipStatePartial.model_validate({'address': address})

    man_out = await support.update_and_commit(manager_id, partial, session)
    # return responses.RedirectResponse(url=f'/ship/view/{manager_id}', status_code=303)
    # return await shipping_page.ship_page(manager=man_out)
    return [
        c.FireEvent(
            event=e.GoToEvent(
                url=f'/ship/view/{manager_id}'
            )
        )
    ]


# @router.post(
#     '/address_form1/{manager_id}',
#     response_model=FastUI,
#     response_model_exclude_none=True
# )
# async def address_form_post1(
#         request: fastapi.Request,
#         manager_id: int,
#         session=fastapi.Depends(am_db.get_session),
#         pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),
# ) -> list[c.AnyComponent]:
#     form = await request.form()
#     address = form.get('address')
#     addy = pf_ext.AddressRecipient.model_validate_json(address)
#     man_in = await support.get_manager(manager_id, session)
#     man_in.state.address = addy
#     man_in.state.candidates = pfcom.get_candidates(addy.postcode)
#     session.add(man_in)
#     session.commit()
#     return await ship_page(manager=man_in)


async def man_in_to_out(man_in: managers.BookingManagerDB) -> managers.BookingManagerOut:
    return managers.BookingManagerOut.model_validate(man_in)


@router.post('/postcode2/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def postcode_post2(
        manager_id: int,
        fetch_address_from_postcode=fastapi.Form(...),
        session=fastapi.Depends(am_db.get_session),
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),
) -> list[c.AnyComponent]:
    pc = fetch_address_from_postcode.upper()

    if shipr_types.is_valid_postcode(pc):
        man_in = await support.get_manager(manager_id, session)
        man_in.state.candidates = pfcom.get_candidates(fetch_address_from_postcode)
        session.add(man_in)
        session.commit()
        alert_dict = {}
    else:
        alert_dict = {f'INVALID POSTCODE : {pc}': 'ERROR'}
        logger.warning(f'Invalid postcode: {pc}')

    return [
        c.FireEvent(
            event=e.GoToEvent(
                url=f'/ship/view/{manager_id}',
                # target='_blank',
            )
        )
    ]
    # return await ship_page_2.shipping_page(
    #     manager_id=manager_id,
    #     session=session,
    #     alert_dict=alert_dict
    # )
    # return [
    #     e.PageEvent(
    #         name='change-form',
    #         # push_path=
    #     )
    # ]

    # return [
    #     c.FireEvent(
    #         event=e.GoToEvent(
    #             url=f'/sl/pcneighbours/{manager_id}/{form.fetch_address_from_postcode}'
    #         )
    #     )
    # ]


@router.post('/postcode/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def postcode_post(
        manager_id: int,
        form: Annotated[ship_forms.PostcodeSelect, fastui_form(ship_forms.PostcodeSelect)],
        session=fastapi.Depends(am_db.get_session),
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),
) -> list[c.AnyComponent]:
    man_in = await support.get_manager(manager_id, session)
    man_in.state.candidates = pfcom.get_candidates(form.fetch_address_from_postcode)
    session.add(man_in)
    session.commit()

    if not shipr_types.is_valid_postcode(form.fetch_address_from_postcode):
        logger.warning(f'Invalid postcode: {form.fetch_address_from_postcode}')
        alertdict: pawui_types.AlertDict = {
            f'INVALID POSTCODE : {form.fetch_address_from_postcode}': 'ERROR'
        }
        return await ship.shipping_page(
            manager_id=manager_id,
            session=session,
            alert_dict=alertdict
        )

        # return await shipping_page.ship_page(manager=man_in, alert_dict=alertdict)

        # return [c.FireEvent(event=e.GoToEvent(url=f'/ship/view/{manager_id}'))]

    # return await ship_page_2.shipping_page(manager_id=manager_id, session=session)
    return [c.FireEvent(event=e.GoToEvent(url=f'/ship/view/{manager_id}'))]

    # return [
    #     c.FireEvent(
    #         event=e.GoToEvent(
    #             url=f'/sl/pcneighbours/{manager_id}/{form.fetch_address_from_postcode}'
    #         )
    #     )
    # ]


# @router.post('/boxes/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
# async def boxes_post(
#         manager_id: int,
#         form: Annotated[BoxesModelForm, fastui_form(BoxesModelForm)],
# ):
#     ...
#     return [c.FireEvent(event=e.GoToEvent(url=f'/ship/view/{manager_id}'))]


# class FormType(_p.BaseModel):
#     boxes: int
#     date: dt.date
#     direction: str
#     address: str


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


# @router.post(
#     '/boxes/{manager_id}',
#     response_model=FastUI,
#     response_model_exclude_none=True
# )
# async def boxes_post(
#         manager_id: int,
#         boxes: int = fastapi.Form(...),
# ):
#     return [
#         c.FireEvent(
#             event=e.GoToEvent(
#                 url=f'/ship/update/{manager_id}/{states.ShipStatePartial(boxes=boxes).model_dump_64()}'
#             ),
#         )
#     ]


# @router.post(
#     '/address_contact/{manager_id}',
#     response_model=FastUI,
#     response_model_exclude_none=True
# )
# async def address_contact_post(
#         manager_id: int,
#         form: Annotated[
#             ship_forms.ContactAndAddressForm, fastui_form(ship_forms.ContactAndAddressForm)],
#         session=fastapi.Depends(am_db.get_session),
# ):
#     man_in = await get_manager(manager_id, session)
#     contact = shipr.models.Contact(
#         business_name=form.business_name,
#         email_address=form.email_address,
#         mobile_phone=form.mobile_phone,
#         contact_name=form.contact_name,
#     )
#     address = shipr.models.AddressRecipient(
#         address_line1=form.address_line1,
#         address_line2=form.address_line2,
#         address_line3=form.address_line3,
#         town=form.town,
#         postcode=form.postcode,
#         country=form.country,
#     )
#     address = address.model_validate(address)
#     contact = contact.model_validate(contact)
#     return [
#         c.FireEvent(
#             event=e.GoToEvent(
#                 url=f'/ship/update/{manager_id}/{man_in.state.update_dump_64_dict(address=address, contact=contact)}'
#             ),
#         )
#     ]

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


@router.post('/full/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def full_post(
        form: Annotated[ship_forms.FullForm, fastui_form(ship_forms.FullForm)],
        manager_id: int,
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),
        session=fastapi.Depends(am_db.get_session),
):
    ...
