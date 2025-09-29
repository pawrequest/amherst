from typing import TYPE_CHECKING

from loguru import logger

from amherst.models.commence_adaptors import CategoryName

if TYPE_CHECKING:
    from amherst.models.amherst_models import AmherstShipableBase

TABLE_REGISTER: dict[str, type['AmherstShipableBase']] = {}


def register_table(cls: type['AmherstShipableBase']) -> type['AmherstShipableBase']:
    TABLE_REGISTER[str(cls.category)] = cls
    logger.debug(f'Registered table model: {cls.category}')
    return cls


def get_table_model(csrname: CategoryName) -> type['AmherstShipableBase'] | None:
    res = TABLE_REGISTER.get(csrname)
    if not res:
        logger.warning(f'No table model found for csrname: {csrname}')
    return res


