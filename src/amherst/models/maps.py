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

# TMPLT_TYPE = Literal['listing', 'detail']
# CURSOR_MAP = {
#     'Hire': {
#         'input_type': AmherstHire,
#         'aliases': HireAliases,
#         # 'template': 'listing_order.html',
#         # 'listing-template': 'listing_order.html',
#         'listing-template': 'listing_generic.html',
#         'detail-template': 'detail_generic.html',
#         # 'detail-template': 'detail_order.html',
#     },
#     'Sale': {
#         'input_type': AmherstSale,
#         'aliases': SaleAliases,
#         # 'template': 'listing_order.html',
#         # 'listing-template': 'listing_order.html',
#         'listing-template': 'listing_generic.html',
#         'detail-template': 'detail_generic.html',
#
#         # 'detail-template': 'detail_order.html',
#     },
#     'Customer': {
#         'input_type': AmherstCustomer,
#         'aliases': CustomerAliases,
#         # 'template': 'listing_customer.html',
#         'listing-template': 'listing_generic.html',
#         # 'listing-template': 'listing_customer.html',
#         'detail-template': 'detail_generic.html',
#     },
#     'Radio Trial': {
#         'input_type': AmherstTrial,
#         'aliases': TrialAliases,
#         'listing-template': 'listing_generic.html',
#         'detail-template': 'detail_generic.html',
#     },
# }


# CsrName = Literal['Hire', 'Sale', 'Customer', 'Trial']
# assert get_args(AmherstTableName) == tuple(CURSOR_MAP.keys())
# logger.debug(f'{tuple(AmherstTableName.__members__)=}')
# logger.debug(f'{tuple(CURSOR_MAP.keys())=}')
# assert tuple(AmherstTableName.__members__) == tuple(CURSOR_MAP.keys())


# async def template_name_from_query(csrname: AmherstTableName = Query(...)):
#     return CURSOR_MAP[csrname]['template']


# async def get_tmplt_name(tmplt_type: TMPLT_TYPE, csrname: AmherstTableName = Path(...)):
#     return CURSOR_MAP[csrname][f'{tmplt_type}-template']


# def get_alias(category: AmherstTableName, field_name):
#     field_name = field_name.upper()
#     aliases = CURSOR_MAP[category]['aliases']
#     if hasattr(aliases, field_name):
#         return getattr(aliases, field_name).value
#     return field_name
