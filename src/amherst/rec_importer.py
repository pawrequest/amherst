import sqlmodel as sqm
from loguru import logger

import shipr
from amherst import shipper
from amherst.models import hire_manager, hire_model
from shipr import ShipState
from shipr.models import pf_shared


def initial_hire_state(
        hire: hire_model.Hire,
        pfcom: shipper.ELClient,
        ship_service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24,
) -> shipr.ShipState:
    try:
        address = pfcom.choose_address(hire.input_address)
    except ValueError as e:
        logger.error(
            f"USING BAD ADDRESS no address at postcode '{hire.input_address.postcode}' for hire {hire.name}: {e}"
        )
        address = hire.input_address

    state = ShipState(
        boxes=hire.boxes,
        ship_date=hire.ship_date,
        ship_service=ship_service,
        contact=hire.contact,
        address=address,
    )
    return state.model_validate(state)


def records_to_managers(
        *records: dict[str, str],
        pfcom: shipper.AmShipper
) -> list[hire_manager.HireManagerDB]:
    managers = []
    for record in records:
        hire_input_ = hire_model.Hire(record=record)
        print(f'importing record {hire_input_.name}')
        hire_input = hire_input_.model_validate(hire_input_)
        state = initial_hire_state(hire_input, pfcom)
        manager_ = hire_manager.HireManagerDB(hire=hire_input, state=state)
        managers.append(manager_.model_validate(manager_))

    return managers
    # session.add_all(managers)
    # session.commit()
    # return True


def add_rec(pfcom, record, session):
    hire_input_ = hire_model.Hire(record=record)
    hire_input = hire_input_.model_validate(hire_input_)
    state = initial_hire_state(hire_input, pfcom)
    manager_ = hire_manager.HireManagerDB(hire=hire_input, state=state)
    manager = manager_.model_validate(manager_)
    session.add(manager)
    session.commit()
    return manager
