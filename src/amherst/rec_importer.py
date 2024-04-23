from loguru import logger
from pydantic import ValidationError

import shipaw
from amherst import shipper
from amherst.models import am_record
from amherst.models.am_record import AmherstRecord


# def initial_state(
#     shipable: AmherstRecord,
# ) -> shipaw.ShipState:
#     el_client = shipper.AmShipper()
#     chosen, candidates = el_client.choose_address(shipable.address)
#     try:
#         return shipaw.ShipState(
#             contact=shipable.contact,
#             address=chosen,
#             ship_date=shipable.send_date,
#             boxes=shipable.boxes,
#             candidates=candidates,
#             reference=shipable.delivery_business,
#             special_instructions='',
#         )
#     except ValidationError as e:
#         logger.exception(e)
#         raise ValueError(f'Error creating initial state: {e}')
