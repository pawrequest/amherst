from __future__ import annotations

import functools
from typing import Literal

from amherst.models.commence_adaptors import HireAliases, SaleAliases
from pycommence.filters import (
    ConditionType,
    ConnectedFieldFilter,
    FieldFilter,
    FilterArray,
    SortOrder,
)
from pycommence.pycmc_types import Connection2

FilterName = Literal['initial', 'pk']


@functools.lru_cache
def get_hire_filter(pk_value: str | None = None):
    res = FilterArray(
        filters={
            1: FieldFilter(
                column=HireAliases.SEND_DATE,
                condition=ConditionType.AFTER,
                value='one month ago'
            ),
            2: FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.BEFORE, value='one month from today'),
            3: FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_CONTAIN, value='Returned'),
        },
        sorts=((HireAliases.SEND_DATE, SortOrder.DESC),),
        logics=['And', 'And'],
    )
    if pk_value:
        res.add_filter(FieldFilter(column=HireAliases.NAME, condition=ConditionType.CONTAIN, value=pk_value))
    return res


@functools.lru_cache
def get_sale_filter(pk_value: str | None = None):
    res = FilterArray(
        filters={
            1: FieldFilter(
                column=SaleAliases.DATE_ORDERED,
                condition=ConditionType.AFTER,
                value='one month ago'
            ),
        },
        sorts=((SaleAliases.DATE_ORDERED, SortOrder.DESC),),
    )
    if pk_value:
        res.add_filter(FieldFilter(column=SaleAliases.NAME, condition=ConditionType.CONTAIN, value=pk_value))
    return res


@functools.lru_cache
def get_customer_filter(pk_value: str | None = None):
    customer_hire_connection = Connection2(name='Has Hired', category='Hire', column='Name')
    customer_sale_connection = Connection2(name='Involves', category='Sale', column='Name')
    customer_hire_filters = [ConnectedFieldFilter.from_fil(f, customer_hire_connection) for f in
                             get_hire_filter().filters.values()]
    customer_sale_filters = [ConnectedFieldFilter.from_fil(f, customer_sale_connection) for f in
                             get_sale_filter().filters.values()]
    assert len(customer_hire_filters) == 3
    assert len(customer_sale_filters) == 1

    if pk_value:
        res = FilterArray(
            filters={
                1: customer_hire_filters[0],
                2: customer_hire_filters[1],
                3: customer_hire_filters[2],
                4: FieldFilter(column=HireAliases.NAME, condition=ConditionType.CONTAIN, value=pk_value),
                5: FieldFilter(column=SaleAliases.NAME, condition=ConditionType.CONTAIN, value=pk_value),
                6: customer_sale_filters[0],
            },
            logics=['And', 'And', 'And', 'Or', 'And'],
        )
    else:
        res = FilterArray(
            filters={
                1: customer_hire_filters[0],
                2: customer_hire_filters[1],
                3: customer_sale_filters[0],
            },
            logics=['And', 'Or'],
        )
    return res


@functools.lru_cache
def get_filter_array(
        csrname,
        pk_value: str | None = None,
) -> FilterArray:
    match csrname:
        case 'Hire':
            return get_hire_filter(pk_value)
        case 'Sale':
            return get_sale_filter(pk_value)
        case 'Customer':
            return get_customer_filter(pk_value)
        case _:
            raise ValueError(f'Unknown cursor name {csrname}')
