import fastapi
from fastapi import Depends
from fastui import FastUI, components as c
from sqlmodel import Session

from amherst import am_db
from amherst.am_db import get_pfc, get_session
from amherst.routers import shipping_page
from amherst.models import managers
from amherst.front.pages.back_funcs import get_manager
from amherst.shipper import AmShipper
from pawdantic.pawui import builders

router = fastapi.APIRouter()


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


@router.get('/get_state/{man_id}')
async def get_manager_json(
        man_id: int,
        session=fastapi.Depends(am_db.get_session),
):
    man_in = await get_manager(man_id, session)

    return man_in.model_dump_json()


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
