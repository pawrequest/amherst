import pydantic
from fastapi import APIRouter, Depends

from amherst.am_db import get_pfc
from amherst.shipper import AmShipper
from shipr.models import pf_ext

router = APIRouter()


# @router.get(
#     "candidate_buttons/{booking_id}/{postcode}",
#     response_model=FastUI,
#     response_model_exclude_none=True
# )
# async def candidate_buttons(
#         booking_id: int,
#         postcode: str,
#         pfcom: AmShipper = Depends(get_pfc),
#         session: Session = Depends(get_session)
# ):
#     return [
#         c.Button(
#             text=can.address_line1,
#             on_click=GoToEvent(
#                 url=f"/hire/update/{booking_id}/{self.boo, address=can)}",
#                 # query={"address": can.model_dump_json()},
#             ),
#         )
#         for can in pfcom.get_candidates(postcode)
#     ]


class CandidatesResponse(pydantic.BaseModel):
    candidates: list[pf_ext.AddressRecipient]


@router.get('/get_cands/{postcode}', response_model=CandidatesResponse)
def get_candidates(postcode: str, pfcom: AmShipper = Depends(get_pfc)):
    candidates = pfcom.get_candidates(postcode)
    return CandidatesResponse(candidates=candidates)
