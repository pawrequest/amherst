from loguru import logger
import shipr
from shipr import ShipState
from shipr.models import pf_shared
from shipr.ship_ui import managers

from amherst import shipper
from amherst.models import hire_model, managers, sale_model, types as am_types


# def initial_hire_state(
#         hire: hire_model.Hire,
#         pfcom: shipper.ELClient,
#         ship_service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24,
# ) -> shipr.ShipState:
#     try:
#         address = pfcom.choose_address(hire.input_address)
#     except ValueError as e:
#         logger.error(
#             f"USING BAD ADDRESS no address at postcode '{hire.input_address.postcode}' for hire {hire.name}: {e}"
#         )
#         address = hire.input_address
# 
#     state = ShipState(
#         boxes=hire.boxes,
#         ship_date=hire.ship_date,
#         ship_service=ship_service,
#         contact=hire.contact,
#         address=address,
#     )
#     return state.model_validate(state)


def initial_state(
        shipable: hire_model.ShipableItem,
        pfcom: shipper.ELClient,
        ship_service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24,
) -> shipr.ShipState:
    try:
        address = pfcom.choose_address(shipable.input_address)
    except ValueError as e:
        logger.error(
            f"USING BAD ADDRESS no address at postcode '{shipable.input_address.postcode}' for hire {shipable.name}: {e}"
        )
        address = shipable.input_address

    state = ShipState(
        boxes=shipable.boxes,
        ship_date=shipable.ship_date,
        ship_service=ship_service,
        contact=shipable.contact,
        address=address,
    )
    return state.model_validate(state)


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
