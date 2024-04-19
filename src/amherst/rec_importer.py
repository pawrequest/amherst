import shipaw
from pydantic import ValidationError

from amherst import shipper
from amherst.models import managers, shipable_item


def initial_state(
    shipable: shipable_item.ShipableRecord,
) -> shipaw.ShipState:
    el_client = shipper.AmShipper()
    address = el_client.choose_address(shipable.input_address)
    candidates = el_client.get_candidates(shipable.postcode)

    reference = shipable.delivery_business
    try:
        return shipaw.ShipState(
            contact=shipable.contact,
            address=address,
            ship_date=shipable.ship_date,
            boxes=shipable.boxes,
            candidates=candidates,
            reference=reference,
            special_instructions="",
        )
    except ValidationError as e:
        raise ValueError(f"Error creating initial state: {e}")


