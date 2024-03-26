import sqlmodel as sqm

import shipr
from amherst.models import managers


class ManagerNotFound(Exception):
    pass


async def get_manager(manager_id: int, session: sqm.Session) -> managers.BookingManagerDB:
    man_in = session.get(managers.BookingManagerDB, manager_id)
    if not isinstance(man_in, managers.BookingManagerDB):
        raise ManagerNotFound()
    return man_in


async def updated_state(man_in, updt):
    return shipr.ShipState.model_validate(
        man_in.state.get_updated(updt)
    )


async def update_and_commit(manager_id, partial, session) -> managers.BookingManagerDB:
    man_in = await get_manager(manager_id, session)
    man_in.state = await updated_state(man_in, partial)
    session.add(man_in)
    session.commit()
    return man_in
