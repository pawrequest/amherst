from __future__ import annotations

from abc import ABC
from typing import Annotated, ClassVar

from pydantic import BaseModel, BeforeValidator, ConfigDict, PlainSerializer

from amherst.models.commence_adaptors import CategoryName

CSV_SEPERATOR = ',\r\n\r\n'


def split_csv(v):
    if isinstance(v, list):
        return v
    if isinstance(v, str):
        return [item.strip() for item in v.split(',') if item.strip()]
    raise ValueError(f'Expected a string, got {type(v)}')


def join_csv(v):
    if isinstance(v, str):
        return v
    if isinstance(v, list):
        return CSV_SEPERATOR.join(v)
    raise ValueError(f'Expected a list, got {type(v)}')


CommaSeparatedStrField = Annotated[
    list[str],
    BeforeValidator(split_csv),
    PlainSerializer(join_csv),
]


class AmherstBase(BaseModel, ABC):
    category: ClassVar[CategoryName]
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
        validate_assignment=True,
    )
