import fastapi
import sqlmodel as sqm

import shipr
from amherst.models import managers


class ManagerNotFound(Exception):
    pass


async def get_manager(manager_id: int, session: sqm.Session):
    man_in = session.get(managers.BookingManagerDB, manager_id)
    if not isinstance(man_in, managers.BookingManagerDB):
        # raise ManagerNotFound()
        raise fastapi.HTTPException(status_code=404, detail='Booking not found')

    return man_in
    # return man_in.model_validate(man_in)


async def update_state(man_in, updt):
    # res= shipr.ShipState.model_validate(
    #     man_in.state.get_updated(updt)
    # )
    # return res

    updated_state_ = man_in.state.get_updated(updt)
    updated_state = shipr.ShipState.model_validate(updated_state_)
    man_in.state = updated_state
    return man_in


async def update_and_commit(manager_id, partial, session) -> managers.BookingManagerOut:
    man_in = await get_manager(manager_id, session)
    updated_state_ = man_in.state.get_updated(partial)
    updated_state = shipr.ShipState.model_validate(updated_state_)
    man_in.state = updated_state
    session.add(man_in)
    session.commit()
    man_out = managers.BookingManagerOut.model_validate(man_in)

    return man_out
