from loguru import logger
import shipr
from amherst import shipper
from amherst.models import managers, shipable_item
from shipr import shipr_types as s_types
from shipr.models import pf_ext, pf_shared


def initial_state(
        shipable: shipable_item.ShipableItem,
        pfcom: shipper.ELClient,
) -> shipr.ShipState:
    state = shipr.ShipStatePartial()
    try:
        state.address = pfcom.choose_address(shipable.input_address)
        state.candidates = pfcom.get_candidates(shipable.input_address.postcode)
    except s_types.ExpressLinkError as e:
        logger.error(
            f"USING BAD ADDRESS no address at postcode '{shipable.input_address.postcode}' for hire {shipable.name}: {e}"
        )
        state.alert_dict = {e.args[0]: 'ERROR'}
        state.address = pf_ext.AddressRecipient(
            address_line1=e.args[0],
            town='',
            postcode=shipable.input_address.postcode,
        )

    state.boxes = shipable.boxes
    state.ship_date = shipable.ship_date
    state.service = pf_shared.ServiceCode.EXPRESS24
    state.contact = shipable.contact
    state.direction = 'out'
    state.reference = state.contact.business_name

    return shipr.ShipState.model_validate(state.model_dump())


def generic_item_to_manager(
        shipable: shipable_item.ShipableItem,
        pfcom: shipper.AmShipper,
) -> managers.BookingManagerDB:
    item = shipable.model_validate(shipable)
    state = initial_state(item, pfcom)

    manager = managers.BookingManagerDB.model_validate(
        managers.BookingManagerDB(item=item, state=state)
    )
    return manager
