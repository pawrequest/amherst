from loguru import logger
from pydantic import ValidationError

import shipaw
from amherst import shipper
from amherst.models import shipable_item


def initial_state(
    shipable: shipable_item.ShipableRecord,
) -> shipaw.ShipState:
    el_client = shipper.AmShipper()
    chosen, candidates = el_client.choose_address(shipable.input_address)
    try:
        return shipaw.ShipState(
            contact=shipable.contact,
            address=chosen,
            ship_date=shipable.ship_date,
            boxes=shipable.boxes,
            candidates=candidates,
            reference=shipable.delivery_business,
            special_instructions='',
        )
    except ValidationError as e:
        logger.exception(e)
        raise ValueError(f'Error creating initial state: {e}')
