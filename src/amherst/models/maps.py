from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from typing import NamedTuple

from fastapi import Query

from amherst.models.amherst_models import AmherstCustomer, AmherstHire, AmherstSale, AmherstTableBase, AmherstTrial
from amherst.models.commence_adaptors import AmherstTableName, CustomerAliases, HireAliases, SaleAliases, TrialAliases
from amherst.models.filters import (
    CUSOMER_CONNECTION,
    DEFAULT_CUSTOMER_FILTER,
    DEFAULT_HIRE_FILTER,
    DEFAULT_SALE_FILTER,
)
from pycommence.filters import FilterArray
from pycommence.pycmc_types import Connection


class AmherstMapping(NamedTuple):
    category: AmherstTableName
    record_model: type(AmherstTableBase)
    aliases: type(StrEnum)
    listing_template: str = 'customers.html'
    detail_template: str = 'hires_sales.html'
    default_filter: FilterArray = FilterArray()
    customer_connection: Connection | None = None
    default_py_filter: Callable[[dict[str, str]], bool] = None


Hire_Map = AmherstMapping(
    category=AmherstTableName.Hire,
    record_model=AmherstHire,
    aliases=HireAliases,
    default_filter=DEFAULT_HIRE_FILTER,
    customer_connection=CUSOMER_CONNECTION,
    # default_py_filter=filter_orders
)

Sale_Map = AmherstMapping(
    category=AmherstTableName.Sale,
    record_model=AmherstSale,
    aliases=SaleAliases,
    default_filter=DEFAULT_SALE_FILTER,
    customer_connection=CUSOMER_CONNECTION,
)

Customer_Map = AmherstMapping(
    category=AmherstTableName.Customer,
    record_model=AmherstCustomer,
    aliases=CustomerAliases,
    default_filter=DEFAULT_CUSTOMER_FILTER,
)

Trial_Map = AmherstMapping(
    category=AmherstTableName.Trial,
    record_model=AmherstTrial,
    aliases=TrialAliases,
)

MODEL_MAPS = {
    AmherstTableName.Hire: Hire_Map,
    AmherstTableName.Sale: Sale_Map,
    AmherstTableName.Customer: Customer_Map,
    AmherstTableName.Trial: Trial_Map,
}


async def mapper_f_q(csrname: AmherstTableName = Query(...)) -> AmherstMapping:
    return MODEL_MAPS[csrname]
