from __future__ import annotations

import functools
from datetime import date, timedelta

from loguru import logger

from amherst.commence_adaptors import HireAliases, HireStatus, SaleAliases
from pycommence.filters import (
    ConditionType,
    ConnectedFieldFilter,
    FieldFilter,
    FilterArray,
    SortOrder,
)
from pycommence.pycmc_types import Connection2, to_cmc_date

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


def cust_init_2():
    hconnect = Connection2(name='Has Hired', category='Hire', column='Name')
    sconnect = Connection2(name='Involves', category='Sale', column='Name')
    hire_con_fils = [
        ConnectedFieldFilter.from_field_fil(f, hconnect) for f in hire_fils_initial_array().filters.values()
    ]
    logger.info(hire_con_fils)
    sale_con_fils = [
        ConnectedFieldFilter.from_field_fil(f, sconnect) for f in sale_fils_initial_array().filters.values()
    ]
    logger.info(sale_con_fils)
    return FilterArray.from_filters(
        *hire_con_fils,
        *sale_con_fils,
        logic='And, And, And, Or',
        sorts=CUSTOMER_SORTS,
    )


def hire_fils_initial_array() -> FilterArray:
    return FilterArray.from_filters(
        *hire_status_fils(), *hire_date_fils(INITIAL_HIRE_START, INITIAL_HIRE_END), sorts=HIRE_SORTS
    )


def sale_fils_initial_array() -> FilterArray:
    return FilterArray.from_filters(*sale_date_fils(INITIAL_SALE_START), sorts=SALE_SORTS)


@functools.lru_cache
def initial_filter(filtername: str) -> FilterArray:
    match filtername:
        case 'Hire':
            return hire_fils_initial_array()
        case 'Sale':
            return sale_fils_initial_array()
        case 'Customer':
            # return customer_initial_array()
            return cust_init_2()
        case _:
            raise ValueError(f'No filter for {filtername}')
