from __future__ import annotations

from enum import StrEnum
from typing import NamedTuple

from fastapi import Path

from amherst.models.amherst_models import AmherstCustomer, AmherstHire, AmherstSale, AmherstTableBase, AmherstTrial
from amherst.models.commence_adaptors import AmherstTableName, CustomerAliases, HireAliases, SaleAliases, TrialAliases


class AmherstMapping(NamedTuple):
    category: AmherstTableName
    record_model: type(AmherstTableBase)
    aliases: type(StrEnum)
    listing_template: str = 'listing_generic.html'
    detail_template: str = 'detail_generic.html'


Hire_Map = AmherstMapping(
    category=AmherstTableName.Hire,
    record_model=AmherstHire,
    aliases=HireAliases,
)

Sale_Map = AmherstMapping(
    category=AmherstTableName.Sale,
    record_model=AmherstSale,
    aliases=SaleAliases,
)

Customer_Map = AmherstMapping(
    category=AmherstTableName.Customer,
    record_model=AmherstCustomer,
    aliases=CustomerAliases,
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

