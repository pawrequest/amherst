from __future__ import annotations

import functools
from datetime import datetime, timedelta
from typing import Literal
from collections.abc import Generator, Sequence

from pydantic import BaseModel

from amherst.models.amherst_models import AmherstCustomer, AmherstOrderBase
from pycommence.filters import (
    ConditionType,
    ConnectedFieldFilter,
    FieldFilter,
    FilterArray,
    SortOrder,
)
from pycommence.pycmc_types import Connection
from amherst.models.commence_adaptors import HireAliases, SaleAliases

FilterName = Literal['hire', 'sale', 'customer']


def filter_orders[T: AmherstOrderBase](recs: list[T]) -> list[T]:
    recs = [r for r in recs if r.send_date > (datetime.now() - timedelta(days=30)).date()]
    recs = [r for r in recs if not r.arranged_out]
    recs = [r for r in recs if 'return' not in r.status.lower()]
    return recs


def filter_orders_dicts(recs: Sequence[dict]) -> Sequence[dict]:
    recs = [r for r in recs if r.get('send_date') > (datetime.now() - timedelta(days=30)).date()]
    recs = [r for r in recs if not r.get('arranged_out')]
    recs = [r for r in recs if 'return' not in r.get('status').lower()]
    return recs


def filter_orders2(records: list[AmherstOrderBase]) -> list[AmherstOrderBase]:
    cutoff_date = (datetime.now() - timedelta(days=30)).date()
    return [
        record
        for record in records
        if record.send_date > cutoff_date and not record.arranged_out and 'return' not in record.status.lower()
    ]


# def filter_orders_gen(recs: Generator[dict[str, str], None, None]) -> Generator[dict[str, str], None, None]:
#     cutoff_date = (datetime.now() - timedelta(days=30)).date()
#     for record in recs:
#         if (
#             datetime.date(record.get('send_date')) > cutoff_date
#             and not record.arranged_out
#             and 'return' not in record.status.lower()
#         ):
#             yield record
#
#     for r in recs:
#         if r.get('send_date') > (datetime.now() - timedelta(days=30)).date():
#             if not r.get('arranged_out'):
#                 if 'return' not in r.get('status').lower():
#                     yield r


def filter_customers(custs: list[AmherstCustomer]) -> list[AmherstCustomer]:
    custs = [c for c in custs if c.hires or c.sales]
    return custs


class FilterMap(BaseModel):
    cmc_filters: tuple[FieldFilter, ...]
    cmc_logics: tuple[str, ...]
    cmc_sorts: tuple[tuple[str, SortOrder], ...]
    filter_array: FilterArray = None


DEFAULT_HIRE_FILTER = FilterArray(
    filters={
        1: FieldFilter(column=HireAliases.STATUS, condition=ConditionType.CONTAIN, value='Booked'),
        2: FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.AFTER, value='one month ago'),
        3: FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.BEFORE, value='one month from today'),
        4: FieldFilter(column=HireAliases.ARRANGED_OUT, condition=ConditionType.NOT),
    },
    sorts=[
        (HireAliases.SEND_DATE, SortOrder.ASC),
    ],
    logics=['And', 'And', 'And'],
)


DEFAULT_SALE_FILTER = FilterArray(
    filters={
        1: FieldFilter(column=SaleAliases.DATE_ORDERED, condition=ConditionType.AFTER, value='one month ago'),
    },
    sorts=[(SaleAliases.DATE_ORDERED, SortOrder.DESC)],
)


HIRE_CONNECTION = Connection(name='Has Hired', category='Hire', column='Name')
SALE_CONNECTION = Connection(name='Involves', category='Sale', column='Name')
CUSOMER_CONNECTION = Connection(name='To', category='Customer', column='Name')


@functools.lru_cache
def get_customer_filter():
    hire_fils = DEFAULT_HIRE_FILTER.filters.values()
    hire_logics = DEFAULT_HIRE_FILTER.logics
    customer_hire_filters = [ConnectedFieldFilter.from_fil(f, HIRE_CONNECTION) for f in hire_fils]
    sale_fils = DEFAULT_SALE_FILTER.filters.values()
    sale_logics = DEFAULT_SALE_FILTER.logics
    customer_sale_filters = [ConnectedFieldFilter.from_fil(f, SALE_CONNECTION) for f in sale_fils]

    return FilterArray(
        filters={
            1: customer_hire_filters[0],
            2: customer_hire_filters[1],
            3: customer_hire_filters[2],
            4: customer_hire_filters[3],
            5: customer_sale_filters[0],
        },
        logics=['And', 'And', 'And', 'Or'],
        # logics=hire_logics + ['Or'] + sale_logics,
    )


DEFAULT_CUSTOMER_FILTER = get_customer_filter()

#
# @functools.lru_cache
# def get_customer_filter2(pk_value: str | None = None):
#     customer_hire_connection = Connection2(name='Has Hired', category='Hire', column='Name')
#     customer_sale_connection = Connection2(name='Involves', category='Sale', column='Name')
#     customer_hire_filters = [
#         ConnectedFieldFilter.from_fil(f, customer_hire_connection) for f in get_hire_filter().filters.values()
#     ]
#     customer_sale_filters = [
#         ConnectedFieldFilter.from_fil(f, customer_sale_connection) for f in get_sale_filter().filters.values()
#     ]
#     assert len(customer_hire_filters) == 3
#     assert len(customer_sale_filters) == 1
#
#     if pk_value:
#         res = FilterArray(
#             filters={
#                 1: customer_hire_filters[0],
#                 2: customer_hire_filters[1],
#                 3: customer_hire_filters[2],
#                 4: FieldFilter(column=HireAliases.NAME, condition=ConditionType.CONTAIN, value=pk_value),
#                 5: FieldFilter(column=SaleAliases.NAME, condition=ConditionType.CONTAIN, value=pk_value),
#                 6: customer_sale_filters[0],
#             },
#             logics=['And', 'And', 'And', 'Or', 'And'],
#         )
#     else:
#         res = FilterArray(
#             filters={
#                 1: customer_hire_filters[0],
#                 2: customer_hire_filters[1],
#                 3: customer_sale_filters[0],
#             },
#             logics=['And', 'Or'],
#         )
#     return res


# @functools.lru_cache
# def get_filter_array(
#     filtername: FilterName,
#     pk_value: str | None = None,
# ) -> FilterArray:
#     match filtername.lower():
#         case 'hire':
#             return get_hire_filter(pk_value)
#         case 'sale':
#             return get_sale_filter(pk_value)
#         case 'customer':
#             return get_customer_filter(pk_value)
#         case _:
#             raise ValueError(f'Unknown cursor name {filtername}')
