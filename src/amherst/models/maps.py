from __future__ import annotations

from abc import ABC
from enum import StrEnum
from typing import Literal

from fastapi import Path, Query

from amherst.models.amherst_models import AmherstCustomer, AmherstHire, AmherstSale, AmherstTableBase, AmherstTrial
from amherst.models.commence_adaptors import AmherstTableName, CustomerAliases, HireAliases, SaleAliases, TrialAliases

TMPLT_TYPE = Literal['listing', 'detail']


class AType(ABC):
    input_type: AmherstTableBase
    aliases: StrEnum
    listing_template: str
    detail_template: str


CURSOR_MAP = {
    'Hire': {
        'input_type': AmherstHire,
        'aliases': HireAliases,
        # 'template': 'listing_order.html',
        # 'listing-template': 'listing_order.html',
        'listing-template': 'listing_generic.html',
        'detail-template': 'detail_generic.html',
        # 'detail-template': 'detail_order.html',
    },
    'Sale': {
        'input_type': AmherstSale,
        'aliases': SaleAliases,
        # 'template': 'listing_order.html',
        # 'listing-template': 'listing_order.html',
        'listing-template': 'listing_generic.html',
        'detail-template': 'detail_generic.html',

        # 'detail-template': 'detail_order.html',
    },
    'Customer': {
        'input_type': AmherstCustomer,
        'aliases': CustomerAliases,
        # 'template': 'listing_customer.html',
        'listing-template': 'listing_generic.html',
        # 'listing-template': 'listing_customer.html',
        'detail-template': 'detail_generic.html',
    },
    'Radio Trial': {
        'input_type': AmherstTrial,
        'aliases': TrialAliases,
        'listing-template': 'listing_generic.html',
        'detail-template': 'detail_generic.html',
    },
}


# CsrName = Literal['Hire', 'Sale', 'Customer', 'Trial']
# assert get_args(AmherstTableName) == tuple(CURSOR_MAP.keys())
# logger.debug(f'{tuple(AmherstTableName.__members__)=}')
# logger.debug(f'{tuple(CURSOR_MAP.keys())=}')
# assert tuple(AmherstTableName.__members__) == tuple(CURSOR_MAP.keys())


async def template_name_from_query(csrname: AmherstTableName = Query(...)):
    return CURSOR_MAP[csrname]['template']


async def get_tmplt_name(tmplt_type: TMPLT_TYPE, csrname: AmherstTableName = Path(...)):
    return CURSOR_MAP[csrname][f'{tmplt_type}-template']


def get_alias(category: AmherstTableName, field_name):
    field_name = field_name.upper()
    aliases = CURSOR_MAP[category]['aliases']
    if hasattr(aliases, field_name):
        return getattr(aliases, field_name).value
    return field_name
