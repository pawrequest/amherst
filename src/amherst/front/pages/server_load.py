from fastapi import APIRouter, Depends
from fastui import FastUI, components as c
from fastui.events import GoToEvent
from sqlmodel import Session

from amherst.database import get_pfc, get_session
from amherst.shipper import AmShipper

router = APIRouter()


@router.get("candidate_buttons/{hire_id}/{postcode}", response_model=FastUI, response_model_exclude_none=True)
async def candidate_buttons(
    hire_id: int, postcode: str, pfcom: AmShipper = Depends(get_pfc), session: Session = Depends(get_session)
):
    return [
        c.Button(
            text=can.address_line1,
            on_click=GoToEvent(
                url=f"/hire/update/{hire_id}",
                query={"address": can.model_dump_json()},
            ),
        )
        for can in pfcom.get_candidates(postcode)
    ]
