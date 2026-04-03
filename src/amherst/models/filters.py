from __future__ import annotations

import functools
from collections.abc import Generator
from datetime import datetime, timedelta
from typing import Literal

from amherst_core.models import AmherstCustomer, AmherstHire, AmherstSale
from loguru import logger
from pycommence.filters import ConditionType, ConnectedFieldFilter, FieldFilter, FilterArray, Sort, SortOrder
from pycommence.pycmc_types import Connection, get_cmc_date

from amherst.models.amherst_base import alias_lookup

FilterVariant = Literal['loose', 'tight']
CUTOFF_DATE = (datetime.now() - timedelta(days=300)).date()


def customer_row_filter_loose(rowgen: Generator[dict[str, str]]) -> Generator[dict[str, str]]:
    for row in rowgen:
        if contacted := row.get(AmherstCustomer.model_fields['date_last_contacted'].alias):
            # if contacted := row.get(CustomerAliases.DATE_LAST_CONTACTED):
            datey = get_cmc_date(contacted)
            if not datey:
                logger.warning(
                    f'Invalid date for {AmherstCustomer.model_fields["date_last_contacted"].alias}: {contacted}'
                )
                # logger.warning(f'Invalid date for {CustomerAliases.DATE_LAST_CONTACTED}: {contacted}')
            if datey < CUTOFF_DATE:
                continue
            yield row


def generator_passthru(rowgen: Generator[dict[str, str]]) -> Generator[dict[str, str]]:
    yield from rowgen


HIRE_SEND_DATE_ALIAS = alias_lookup(AmherstHire, 'send_date')

HIRE_ARRAY_TIGHT = FilterArray(
    filters={
        1: FieldFilter(column=alias_lookup(AmherstHire, 'status'), condition=ConditionType.CONTAIN, value='Booked'),
        2: FieldFilter(column=HIRE_SEND_DATE_ALIAS, condition=ConditionType.AFTER, value='one week ago'),
        3: FieldFilter(
            column=HIRE_SEND_DATE_ALIAS,
            condition=ConditionType.BEFORE,
            value='one week from today',
        ),
        4: FieldFilter(column=alias_lookup(AmherstHire, 'arranged_out'), condition=ConditionType.NOT),
    },
    sorts=[Sort(column=HIRE_SEND_DATE_ALIAS, order=SortOrder.ASC)],
    # sorts=[
    #     (HireAliases.SEND_DATE, SortOrder.ASC),
    # ],
    logics=['And', 'And', 'And'],
)
#
#
# HIRE_ARRAY_TIGHT = FilterArray(
#     filters={
#         1: FieldFilter(column=HireAliases.STATUS, condition=ConditionType.CONTAIN, value='Booked'),
#         2: FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.AFTER, value='one week ago'),
#         3: FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.BEFORE, value='one week from today'),
#         4: FieldFilter(column=HireAliases.ARRANGED_OUT, condition=ConditionType.NOT),
#     },
#     sorts=[Sort(column=HireAliases.SEND_DATE, order=SortOrder.ASC)],
#     # sorts=[
#     #     (HireAliases.SEND_DATE, SortOrder.ASC),
#     # ],
#     logics=['And', 'And', 'And'],
# )


HIRE_ARRAY_LOOSE = FilterArray(
    filters={
        1: FieldFilter(column=HIRE_SEND_DATE_ALIAS, condition=ConditionType.AFTER, value='six month ago'),
        2: FieldFilter(column=HIRE_SEND_DATE_ALIAS, condition=ConditionType.BEFORE, value='three month from today'),
        # 2: FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.BETWEEN, value='six months ago, three months from today'),
    },
    sorts=[Sort(column=HIRE_SEND_DATE_ALIAS, order=SortOrder.ASC)],
    logics=['And'],
)

SALE_BOOKED_DATE_ALIAS = alias_lookup(AmherstSale, 'booking_date')

SALE_ARRAY_TIGHT = FilterArray(
    filters={
        1: FieldFilter(column=SALE_BOOKED_DATE_ALIAS, condition=ConditionType.AFTER, value='one month ago'),
        # 1: FieldFilter(column=SaleAliases.DATE_ORDERED, condition=ConditionType.AFTER, value='one month ago'),
    },
    sorts=[Sort(column=SALE_BOOKED_DATE_ALIAS, order=SortOrder.DESC)],
    # sorts=[(SaleAliases.DATE_ORDERED, SortOrder.DESC)],
)

SALE_ARRAY_LOOSE = SALE_ARRAY_TIGHT

HIRE_CONNECTION = Connection(name='Has Hired', category='Hire', column='Name')
SALE_CONNECTION = Connection(name='Involves', category='Sale', column='Name')
CUSOMER_CONNECTION = Connection(name='To', category='Customer', column='Name')


@functools.lru_cache
def customer_array_tight():
    hire_fils = HIRE_ARRAY_TIGHT.filters.values()
    customer_hire_filters = [ConnectedFieldFilter.from_fil(f, HIRE_CONNECTION) for f in hire_fils]
    sale_fils = SALE_ARRAY_TIGHT.filters.values()
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


CUSTOMER_ARRAY_TIGHT = customer_array_tight()

CUSTOMER_ARRAY_LOOSE = FilterArray(
    filters={
        1: FieldFilter(
            column=AmherstCustomer.model_fields['date_last_contacted'].alias,
            condition=ConditionType.AFTER,
            value='one year ago',
        ),
    },
    logics=['And'],
)
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
