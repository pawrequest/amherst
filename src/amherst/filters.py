from __future__ import annotations

import functools
from datetime import date, timedelta

from fastapi import Path

from amherst.commence_adaptors import HireAliases, HireStatus, SaleAliases
from pycommence.filters import (
    ConditionType,
    FieldFilter,
    FilterArray,
    SortOrder,
    field_fil_to_confil,
)
from pycommence.pycmc_types import Connection2, to_cmc_date

CUSTOMER_SORTS = None

SALE_SORTS = ((SaleAliases.DATE_ORDERED, SortOrder.DESC),)

HIRE_SORTS = ((HireAliases.SEND_DATE, SortOrder.DESC),)


def hire_date_fils(start_date: date, end_date: date) -> tuple[FieldFilter, ...]:
    fils = (
        FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.AFTER, value=to_cmc_date(start_date)),
    )
    if end_date:
        fils += (FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.BEFORE, value=to_cmc_date(end_date)),)
    return fils


def hire_status_fils() -> tuple[FieldFilter, ...]:
    return (
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
    )


def sale_date_fils(sale_start):
    return (FieldFilter(column=SaleAliases.DATE_ORDERED, condition=ConditionType.AFTER, value=to_cmc_date(sale_start)),)


def customer_hire_fils(hire_start, hire_end):
    connect = Connection2(name='Has Hired', category='Hire', column='Name')
    fils = (hire_status_fils() + hire_date_fils(hire_start, hire_end))
    return [field_fil_to_confil(f, connect) for f in fils]


# def custoemr_fils_logic(hire_start, hire_end, sale_start) -> tuple[tuple[ConnectedFieldFilter, ...], str]:
#     return (
#         (
#             ConnectedFieldFilter(
#                 column='Has Hired',
#                 connection_category='Hire',
#                 connected_column='Send Out Date',
#                 condition=ConditionType.AFTER,
#                 value=to_cmc_date(hire_start),
#             ),
#             ConnectedFieldFilter(
#                 column='Has Hired',
#                 connection_category='Hire',
#                 connected_column='Send Out Date',
#                 condition=ConditionType.BEFORE,
#                 value=to_cmc_date(hire_end),
#             ),
#             ConnectedFieldFilter(
#                 column='Involves',
#                 connection_category='Sale',
#                 connected_column='Date Ordered',
#                 condition=ConditionType.AFTER,
#                 value=to_cmc_date(sale_start),
#             ),
#         ),
#         'And, Or',
#     )


def customer_sales_fils(start_date: date):
    connect = Connection2(name='Involves', category='Sale', column='Name')
    return [field_fil_to_confil(f, connect) for f in sale_date_fils(start_date)]


def customer_initial_array(hire_start: date, hire_end: date, sale_start: date) -> FilterArray:
    return FilterArray.from_filters(
        *customer_hire_fils(hire_start, hire_end),
        *customer_sales_fils(sale_start),
        logic='And, Or',
        sorts=CUSTOMER_SORTS
    )


def hire_fils_initial_array(start_date: date, end_date: date) -> FilterArray:
    return FilterArray.from_filters(*hire_status_fils(), *hire_date_fils(start_date, end_date), sorts=HIRE_SORTS)


def sale_fils_initial_array(sale_start: date) -> FilterArray:
    return FilterArray.from_filters(*sale_date_fils(sale_start), sorts=SALE_SORTS)


@functools.lru_cache
def initial_filter(filtername: str) -> FilterArray:
    hire_start = date.today() - timedelta(days=30)
    hire_end = date.today() + timedelta(days=30)
    sale_start = date.today() - timedelta(days=30)

    match filtername:
        case 'Hire':
            return hire_fils_initial_array(hire_start, hire_end)
        case 'Sale':
            return sale_fils_initial_array(sale_start)
        case 'Customer':
            return customer_initial_array(hire_start, hire_end, sale_start)
        case _:
            raise ValueError(f'No filter for {filtername}')

    # res = FilterArray.from_filters(*fils, sorts=sorts, logic=logic)
    # return res


# def filter_csrname_2year(csrname: str = Path()) -> FilterArray:
#     match csrname:
#         case 'Hire':
#             fils = (date.today() - timedelta(days=365 * 2), date.today())
