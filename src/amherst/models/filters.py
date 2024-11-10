from __future__ import annotations

import functools
from typing import Literal

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


DEFAULT_HIRE_FILTER = FilterArray(
    filters={
        1: FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.AFTER, value='one month ago'),
        2: FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.BEFORE, value='one month from today'),
        3: FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_CONTAIN, value='return'),
        4: FieldFilter(column=HireAliases.ARRANGED_OUT, condition=ConditionType.NOT),
        # 4: FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.CANCELLED),
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


CUSTOMER_HIRE_CONNECTION = Connection(name='Has Hired', category='Hire', column='Name')
CUSTOMER_SALE_CONNECTION = Connection(name='Involves', category='Sale', column='Name')
HIRE_CUSOMER_CONNECTION = Connection(name='To', category='Customer', column='Name')
SALE_CUSOMER_CONNECTION = Connection(name='To', category='Customer', column='Name')


@functools.lru_cache
def get_customer_filter():
    hire_fils = DEFAULT_HIRE_FILTER.filters.values()
    hire_logics = DEFAULT_HIRE_FILTER.logics
    customer_hire_filters = [ConnectedFieldFilter.from_fil(f, CUSTOMER_HIRE_CONNECTION) for f in hire_fils]
    sale_fils = DEFAULT_SALE_FILTER.filters.values()
    sale_logics = DEFAULT_SALE_FILTER.logics
    customer_sale_filters = [ConnectedFieldFilter.from_fil(f, CUSTOMER_SALE_CONNECTION) for f in sale_fils]
    # assert len(customer_hire_filters) == 4
    # assert len(customer_sale_filters) == 1

    return FilterArray(
        filters={
            1: customer_hire_filters[0],
            2: customer_hire_filters[1],
            3: customer_hire_filters[2],
            4: customer_hire_filters[2],  # dupe to make logics work?
            5: customer_sale_filters[0],
        },
        logics=hire_logics + ['Or'] + sale_logics,
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
