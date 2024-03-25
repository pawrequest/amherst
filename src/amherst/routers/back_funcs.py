import sqlmodel as sqm

from amherst.models import managers


class ManagerNotFound(Exception):
    pass


async def get_manager(manager_id: int, session: sqm.Session) -> managers.BookingManagerDB:
    man_in = session.get(managers.BookingManagerDB, manager_id)
    if not isinstance(man_in, managers.BookingManagerDB):
        raise ManagerNotFound()
    return man_in
