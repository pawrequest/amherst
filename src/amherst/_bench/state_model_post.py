import typing as _t

import fastapi
from fastapi import APIRouter, responses
from fastui import FastUI
from fastui.forms import fastui_form

from amherst import am_db, shipper
from amherst.front import support
from shipaw.ship_ui import states as ship_states

router = APIRouter()


@router.post('/update_state/{manager_id}', response_model=FastUI, response_model_exclude_none=True)
async def state_post(
        manager_id: int,
        form: _t.Annotated[
            ship_states.ShipStatePartial, fastui_form(ship_states.ShipStatePartial)],
        pfcom: shipper.AmShipper = fastapi.Depends(am_db.get_el_client),
        session=fastapi.Depends(am_db.get_session),

):
    update = ship_states.ShipStatePartial.model_validate(form.model_dump())
    if update.address.postcode:
        update.candidates = pfcom.get_candidates(update.address.postcode)
    await support.update_and_commit(manager_id, update, session)
    return responses.RedirectResponse(url=f'/ship/select/{manager_id}')
