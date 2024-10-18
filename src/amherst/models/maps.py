from __future__ import annotations


from fastapi import Path, Query

from amherst.config import logger
# from amherst.back.search_paginate import CsrName
from amherst.models.amherst_models import AmherstCustomer, AmherstHire, AmherstSale, AmherstTrial
from amherst.models.commence_adaptors import AmherstTableName, CustomerAliases, HireAliases, SaleAliases, TrialAliases

CURSOR_MAP = {
    'Hire': {
        'input_type': AmherstHire,
        'aliases': HireAliases,
        'template': 'orders.html',
    },
    'Sale': {
        'input_type': AmherstSale,
        'aliases': SaleAliases,
        'template': 'orders.html',
    },
    'Customer': {
        'input_type': AmherstCustomer,
        'aliases': CustomerAliases,
        'template': 'customer.html',
    },
    'Radio Trial': {
        'input_type': AmherstTrial,
        'aliases': TrialAliases,
        'template': 'trial.html',
    },
}

# CsrName = Literal['Hire', 'Sale', 'Customer', 'Trial']
# assert get_args(AmherstTableName) == tuple(CURSOR_MAP.keys())
logger.debug(f'{tuple(AmherstTableName.__members__)=}')
logger.debug(f'{tuple(CURSOR_MAP.keys())=}')
# assert tuple(AmherstTableName.__members__) == tuple(CURSOR_MAP.keys())


async def template_name_from_query(csrname: AmherstTableName = Query(...)):
    return CURSOR_MAP[csrname]['template']


async def template_name_from_path(csrname: AmherstTableName = Path(...)):
    return CURSOR_MAP[csrname]['template']


def get_alias(category: AmherstTableName, field_name):
    field_name = field_name.upper()
    aliases = CURSOR_MAP[category]['aliases']
    if hasattr(aliases, field_name):
        return getattr(aliases, field_name).value
    return field_name
