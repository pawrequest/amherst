from __future__ import annotations

import functools
from datetime import date, timedelta
from typing import Literal

from amherst.models.commence_adaptors import HireAliases, HireStatus, SaleAliases
from pycommence.filters import (
    ConditionType,
    ConnectedFieldFilter,
    FieldFilter,
    FilterArray,
    SortOrder,
)
from pycommence.pycmc_types import Connection2, to_cmc_date

FilterName = Literal['initial_hire', 'initial_sale', 'initial_customer']

CUSTOMER_SORTS = None
SALE_SORTS = ((SaleAliases.DATE_ORDERED, SortOrder.DESC),)
HIRE_SORTS = ((HireAliases.SEND_DATE, SortOrder.DESC),)

INITIAL_HIRE_START = date.today() - timedelta(days=30)
INITIAL_HIRE_END = date.today() + timedelta(days=30)
INITIAL_SALE_START = date.today() - timedelta(days=30)


@functools.lru_cache
def hire_date_fils(start_date: date, end_date: date | None = None) -> tuple[FieldFilter, ...]:
    fils = (FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.AFTER, value=to_cmc_date(start_date)),)
    if end_date:
        fils += (
            FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.BEFORE, value=to_cmc_date(end_date)),
        )
    return fils


@functools.lru_cache
def hire_status_fils() -> tuple[FieldFilter, ...]:
    return (
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
    )


@functools.lru_cache
def sale_date_fils(sale_start):
    return (FieldFilter(column=SaleAliases.DATE_ORDERED, condition=ConditionType.AFTER, value=to_cmc_date(sale_start)),)


@functools.lru_cache
def cust_init_2():
    hconnect = Connection2(name='Has Hired', category='Hire', column='Name')
    sconnect = Connection2(name='Involves', category='Sale', column='Name')
    hire_con_fils = [
        ConnectedFieldFilter.from_field_fil(f, hconnect) for f in hire_fils_initial_array().filters.values()
    ]
    sale_con_fils = [
        ConnectedFieldFilter.from_field_fil(f, sconnect) for f in sale_fils_initial_array().filters.values()
    ]
    return FilterArray.from_filters(
        *hire_con_fils,
        *sale_con_fils,
        logics=['And', 'And', 'And', 'Or'],
        sorts=CUSTOMER_SORTS,
    )


@functools.lru_cache
def hire_fils_initial_array() -> FilterArray:
    return FilterArray.from_filters(
        *hire_status_fils(), *hire_date_fils(INITIAL_HIRE_START, INITIAL_HIRE_END), sorts=HIRE_SORTS
    )


@functools.lru_cache
def sale_fils_initial_array() -> FilterArray:
    return FilterArray.from_filters(*sale_date_fils(INITIAL_SALE_START), sorts=SALE_SORTS)
