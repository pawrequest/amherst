from __future__ import annotations

import functools
from datetime import date, timedelta

from amherst.commence_adaptors import HireAliases, HireStatus, SaleAliases
from pycommence.filters import (
    ConditionType,
    ConnectedFieldFilter,
    FieldFilter,
    FilterArray,
    SortOrder,
)
from pycommence.pycmc_types import to_cmc_date

CUSTOMER_SORTS = None

SALE_SORTS = ((SaleAliases.DATE_ORDERED, SortOrder.DESC),)

HIRE_SORTS = ((HireAliases.SEND_DATE, SortOrder.DESC),)
INITIAL_HIRE_START = date.today() - timedelta(days=30)
INITIAL_HIRE_END = date.today() + timedelta(days=30)
INITIAL_SALE_START = date.today() - timedelta(days=30)


def hire_date_fils(start_date: date, end_date: date | None = None) -> tuple[FieldFilter, ...]:
    fils = (FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.AFTER, value=to_cmc_date(start_date)),)
    if end_date:
        fils += (
            FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.BEFORE, value=to_cmc_date(end_date)),
        )
    return fils


def hire_status_fils() -> tuple[FieldFilter, ...]:
    return (
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
    )


def sale_date_fils(sale_start):
    return (FieldFilter(column=SaleAliases.DATE_ORDERED, condition=ConditionType.AFTER, value=to_cmc_date(sale_start)),)


def customer_initial_array(hire_start: date, hire_end: date, sale_start: date) -> FilterArray:
    return FilterArray.from_filters(
        ConnectedFieldFilter(
            column='Has Hired',
            connection_category='Hire',
            connected_column='Send Out Date',
            condition=ConditionType.AFTER,
            value=to_cmc_date(hire_start),
        ),
        ConnectedFieldFilter(
            column='Has Hired',
            connection_category='Hire',
            connected_column='Send Out Date',
            condition=ConditionType.BEFORE,
            value=to_cmc_date(hire_end),
        ),
        ConnectedFieldFilter(
            column='Involves',
            connection_category='Sale',
            connected_column='Date Ordered',
            condition=ConditionType.AFTER,
            value=to_cmc_date(sale_start),
        ),
        logic='And, Or',
        sorts=CUSTOMER_SORTS,
    )


def hire_fils_initial_array(start_date: date, end_date: date) -> FilterArray:
    return FilterArray.from_filters(*hire_status_fils(), *hire_date_fils(start_date, end_date), sorts=HIRE_SORTS)


def sale_fils_initial_array(sale_start: date) -> FilterArray:
    return FilterArray.from_filters(*sale_date_fils(sale_start), sorts=SALE_SORTS)


@functools.lru_cache
def initial_filter(filtername: str) -> FilterArray:
    match filtername:
        case 'Hire':
            return hire_fils_initial_array(INITIAL_HIRE_START, INITIAL_HIRE_END)
        case 'Sale':
            return sale_fils_initial_array(INITIAL_SALE_START)
        case 'Customer':
            return customer_initial_array(INITIAL_HIRE_START, INITIAL_HIRE_END, INITIAL_SALE_START)
        case _:
            raise ValueError(f'No filter for {filtername}')
