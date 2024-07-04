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
    field_fil_to_confil,
)
from pycommence.pycmc_types import Connection2, to_cmc_date


def hire_fils(start_date: date, end_date: date) -> tuple[FieldFilter, ...]:
    return (
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
        FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.AFTER, value=to_cmc_date(start_date)),
        FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.BEFORE, value=to_cmc_date(end_date)),
    )


def sale_fils(sale_start):
    return (FieldFilter(column=SaleAliases.DATE_ORDERED, condition=ConditionType.AFTER, value=to_cmc_date(sale_start)),)


def customer_hire_fils(hire_start, hire_end):
    connect = Connection2(name='Has Hired', category='Hire', column='Name')
    return [field_fil_to_confil(f, connect) for f in hire_fils(hire_start, hire_end)]


def custoemr_fils_logic(hire_start, hire_end, sale_start) -> tuple[tuple[ConnectedFieldFilter, ...], str]:
    return (
        (
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
        ),
        'And, Or',
    )


def customer_sales_fils(start_date: date):
    connect = Connection2(name='Involves', category='Sale', column='Name')
    return [field_fil_to_confil(f, connect) for f in sale_fils(start_date)]


def customer_fils(hire_start, hire_end, sale_start):
    return *customer_hire_fils(hire_start, hire_end), *customer_sales_fils(sale_start)


@functools.lru_cache
def initial_filter(filtername: str) -> FilterArray:
    hire_start = date.today() - timedelta(days=30)
    hire_end = date.today() + timedelta(days=30)
    sale_start = date.today() - timedelta(days=30)

    match filtername:
        case 'Hire':
            fils = hire_fils(hire_start, hire_end)
            logic = None
            sorts = ((HireAliases.SEND_DATE, SortOrder.DESC),)

        case 'Sale':
            fils = sale_fils(sale_start)
            logic = None
            sorts = ((SaleAliases.DATE_ORDERED, SortOrder.DESC),)

        case 'Customer':
            fils, logic = custoemr_fils_logic(hire_start, hire_end, sale_start)
            sorts = None

        case _:
            raise ValueError(f'No filter for {filtername}')

    res = FilterArray.from_filters(*fils, sorts=sorts, logic=logic)
    return res
