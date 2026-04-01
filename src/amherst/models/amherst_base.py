from __future__ import annotations

from abc import ABC
from typing import ClassVar
from loguru import logger
from pydantic import BaseModel, ConfigDict

from amherst.models.commence_adaptors import CategoryName


class AmherstBase(BaseModel, ABC):
    category: ClassVar[CategoryName]
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
    )


def alias_lookup(cls: type[BaseModel], field_name: str) -> str:
    try:
        return cls.model_fields[field_name].alias
    except KeyError:
        logger.warning(f'Alias for {field_name} not found in model {cls.__name__}. Returning field name.')
        return field_name
