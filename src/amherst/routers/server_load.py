import fastapi
from fastapi import Depends
from fastui import FastUI
from fastui import components as c
from sqlmodel import Session

import amherst.app_file
import amherst.front
import amherst.routers.back_funcs
from amherst import am_db, shipper
from amherst.am_db import get_pfc, get_session
from amherst.front.pages import shipping_page
from amherst.models import managers
from amherst.routers.back_funcs import get_manager
from amherst.shipper import AmShipper
from pawdantic.pawui import builders
from shipr.models import dynamic

router = fastapi.APIRouter()


@router.get('/booking_form/{man_id}', response_model=FastUI, response_model_exclude_none=True)
async def booking_form(
        man_id: int,
        session=fastapi.Depends(am_db.get_session),
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_pfc),
) -> list[c.AnyComponent]:
    man_in = await amherst.routers.back_funcs.get_manager(man_id, session)
    candidates = pfcom.get_candidates(man_in.state.address.postcode)
    booking_form_ = dynamic.make_booking_form_type(candidates=candidates)
    res = [c.Div(
        components=[
            c.ModelForm(
                model=booking_form_,
                submit_url=f'/api/forms/book_form/{man_id}',
            ),
        ],
        class_name='row'
    ),
    ]
    return res


@router.get('/check_state/{man_id}', response_model=FastUI, response_model_exclude_none=True)
async def check_state(
        man_id: int,
        session=fastapi.Depends(am_db.get_session),
) -> list[c.AnyComponent]:
    man_in = await get_manager(man_id, session)
    texts = builders.dict_strs_texts(
        man_in.state.model_dump(exclude={'candidates'}),
        with_keys='YES'
    )
    return [c.Div(
        components=builders.list_of_divs(
            components=texts
        ),
        class_name='row'
    )]


@router.get(
    '/pcneighbours/{booking_id}/{postcode}',
    response_model=FastUI,
    response_model_exclude_none=True
)
async def pcneighbours(
        booking_id: int,
        postcode: str,
        pfcom: AmShipper = Depends(get_pfc),
        session: Session = Depends(get_session),
):
    man_in = await get_manager(booking_id, session)
    man_out = managers.BookingManagerOut.model_validate(man_in)
    candidates = pfcom.get_candidates(postcode)
    return await shipping_page.address_chooser2(
        manager=man_out,
        candidates=candidates
    )
