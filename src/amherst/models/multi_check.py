import functools
from typing import Annotated

from pandas import DataFrame
from pydantic import BaseModel, BeforeValidator, ConfigDict
from sqlalchemy import Column, JSON
from sqlmodel import Field, SQLModel

from amherst.commence_adaptors import CustomerAliases, HireAliases, SaleAliases


def dataframe_to_json(v) -> str:
    if isinstance(v, DataFrame):
        return v.to_json()
    return v


DataFrameJson = Annotated[str, BeforeValidator(dataframe_to_json)]


class Multi(SQLModel, table=False):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    category: str
    df: DataFrameJson


class MultiDB(Multi, table=True):
    id: int | None = Field(default=None, primary_key=True)
    df: DataFrameJson = Field(..., sa_column=Column(JSON))


class Multi2(BaseModel):
    ...


@functools.lru_cache
def get_enum_key(category: str):
    if category == 'Customer':
        return CustomerAliases
    elif category == 'Hire':
        return HireAliases
    elif category == 'Sale':
        return SaleAliases
    else:
        raise ValueError(f'Invalid category: {category}')


class ARecord(SQLModel, table=False):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    category: str
    data: dict

    def get_data(self, key: str):
        return self.data[get_enum_key(self.category)[key]]

class ARecordDB(ARecord, table=True):
    id: int | None = Field(default=None, primary_key=True)
    data: dict = Field(..., sa_column=Column(JSON))
