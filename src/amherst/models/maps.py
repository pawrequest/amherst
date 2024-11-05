from __future__ import annotations

from enum import StrEnum
from typing import NamedTuple

from fastapi import Path

from amherst.models.amherst_models import AmherstCustomer, AmherstHire, AmherstSale, AmherstTableBase, AmherstTrial
from amherst.models.commence_adaptors import AmherstTableName, CustomerAliases, HireAliases, SaleAliases, TrialAliases
from amherst.models.filters import DEFAULT_HIRE_FILTER, DEFAULT_SALE_FILTER, DEFAULT_CUSTOMER_FILTER
from pycommence.filters import FilterArray


class AmherstMapping(NamedTuple):
    category: AmherstTableName
    record_model: type(AmherstTableBase)
    aliases: type(StrEnum)
    listing_template: str = 'listing_generic.html'
    detail_template: str = 'detail_generic.html'
    default_filter: FilterArray = FilterArray()


Hire_Map = AmherstMapping(
    category=AmherstTableName.Hire,
    record_model=AmherstHire,
    aliases=HireAliases,
    default_filter=DEFAULT_HIRE_FILTER,
)

Sale_Map = AmherstMapping(
    category=AmherstTableName.Sale,
    record_model=AmherstSale,
    aliases=SaleAliases,
    default_filter=DEFAULT_SALE_FILTER,
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

CMAP = {
    AmherstTableName.Hire: Hire_Map,
    AmherstTableName.Sale: Sale_Map,
    AmherstTableName.Customer: Customer_Map,
    AmherstTableName.Trial: Trial_Map,
}


async def listing_template_name(csrname: AmherstTableName = Path(...)):
    return CMAP[csrname].listing_template


async def detail_template_name(csrname: AmherstTableName = Path(...)):
    return CMAP[csrname].detail_template


async def record_model(csrname: AmherstTableName = Path(...)) -> type(AmherstTableBase):
    return CMAP[csrname].record_model


async def table_type_from_name_path(csrname: AmherstTableName = Path(...)) -> AmherstTableBase:
    return CMAP[csrname].record_model
