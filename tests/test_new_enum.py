import datetime
from abc import ABC

import pycommence
import pydantic as _p
import pytest
from pydantic import AliasChoices, ConfigDict, Field

type OrDict[T] = T | dict[str, T]

home_data = {
    'Customer': 'Test',
    'Hire': 'Test Customer - 2/21/2024 ref 43383',
    'Sale': 'Test - 22/10/2022 ref 1',
}


@pytest.mark.parametrize("key, name", home_data.items())
def test_smth(key, name):
    py_com = pycommence.PyCommence.from_table_name(key)
    record = py_com.one_record(name)
    val = ShipableRecord.model_validate(record)
    ...


class ShipableRecord(_p.BaseModel, ABC):
    model_config = ConfigDict(
        extra='ignore',
    )
    name: str = Field(..., alias='Name')
    customer: str = Field(..., validation_alias=AliasChoices('To Customer', 'Name'))
    send_out_date: str = Field(datetime.date.today(), alias='Send Out Date')
    boxes: int = Field(1, alias='Boxes')
    contact: str = Field(..., validation_alias=AliasChoices('Delivery Contact', 'Deliv Contact'))
    business: str = Field(..., validation_alias=AliasChoices('Delivery Name', 'Deliv Name', 'Customer', 'To Customer'))
    telephone: str = Field(..., validation_alias=AliasChoices('Delivery Tel', 'Deliv Telephone', 'Delivery Telephone'))
    email: str = Field(..., validation_alias=AliasChoices('Delivery Email', 'Deliv Email'))
    address: str = Field(..., validation_alias=AliasChoices('Delivery Address', 'Deliv Address'))
    postcode: str = Field(..., validation_alias=AliasChoices('Delivery Postcode', 'Deliv Postcode'))
