from loguru import logger

import shipr
from amherst import shipper
from amherst.models import hire_model, managers
from shipr import types as s_types
from shipr.models import pf_ext, pf_shared


def initial_state(
        shipable: hire_model.ShipableItem,
        pfcom: shipper.ELClient,
        ship_service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24,
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
    state.ship_service = ship_service
    state.contact = shipable.contact
    state.direction = 'OUTBOUND'

    return shipr.ShipState.model_validate(state.model_dump())


# def initial_state2(
#         shipable: am_types.Shipable,
#         pfcom: shipper.ELClient,
#         ship_service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24,
# ) -> shipr.ShipState:
#     try:
#         address = pfcom.choose_address(shipable.input_address)
#     except ValueError as e:
#         logger.error(
#             f"USING BAD ADDRESS no address at postcode '{shipable.input_address.postcode}' for hire {shipable.name}: {e}"
#         )
#         address = shipable.input_address
# 
#     state = ShipState(
#         boxes=shipable.boxes,
#         ship_date=shipable.ship_date,
#         ship_service=ship_service,
#         contact=shipable.contact,
#         address=address,
#     )
#     return state.model_validate(state)


# def records_to_managers(
#         *records: dict[str, str],
#         model_type: _t.Union[type(hire_model.Hire), type(sale_model.Sale)],
#         pfcom: shipper.AmShipper
# ) -> list[managers.BookingManagerDB]:
#     managers = []
#     for record in records:
#         input_mod = model_type(record=record)
#         input_val = input_mod.model_validate(input_mod)
#         state = initial_state(input_val, pfcom)
#         manager_ = managers.BookingManagerDB(hire=input_val, state=state)
#         managers.append(manager_.model_validate(manager_))
#
#     return managers
#     # session.add_all(managers)
#     # session.commit()
#     # return True


def generic_item_to_manager(
        shipable: hire_model.ShipableItem,
        pfcom: shipper.AmShipper,
) -> managers.BookingManagerDB:
    item = shipable.model_validate(shipable)
    state = initial_state(item, pfcom)
    manager_ = managers.BookingManagerDB(item=item, state=state)
    manager = manager_.model_validate(manager_)
    return manager

# def hire_records_to_managers(
#         *records: dict[str, str],
#         pfcom: shipper.AmShipper
# ) -> list[managers.BookingManagerDB]:
#     managers = []
#     for record in records:
#         hire_input_ = hire_model.Hire(record=record)
#         print(f'importing record {hire_input_.name}')
#         hire_input = hire_input_.model_validate(hire_input_)
#         state = initial_hire_state(hire_input, pfcom)
#         manager_ = managers.BookingManagerDB(hire=hire_input, state=state)
#         managers.append(manager_.model_validate(manager_))
# 
#     return managers


# def sale_records_to_managers(
#         *records: dict[str, str],
#         pfcom: shipper.AmShipper
# ) -> list[manager2.SaleManagerDB]:
#     managers = []
#     for record in records:
#         sale_ = sale_model.Sale(record=record)
#         print(f'importing record {sale_.name}')
#         sale = sale_.model_validate(sale_)
#         state = initial_state(sale, pfcom)
#         manager_ = manager2.SaleManagerDB(sale=sale, state=state)
#         managers.append(manager_.model_validate(manager_))
# 
#     return managers

# def add_rec(pfcom, record, session):
#     hire_input_ = hire_model.Hire(record=record)
#     hire_input = hire_input_.model_validate(hire_input_)
#     state = initial_hire_state(hire_input, pfcom)
#     manager_ = managers.BookingManagerDB(hire=hire_input, state=state)
#     manager = manager_.model_validate(manager_)
#     session.add(manager)
#     session.commit()
#     return manager
