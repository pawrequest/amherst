from __future__ import annotations

import functools
from datetime import date, timedelta

from amherst.commence_adaptors import HireAliases, HireStatus, SaleAliases
from pycommence.filters import ConditionType, ConnectedFieldFilter, FieldFilter, FilterArray, SortOrder
from pycommence.pycmc_types import to_cmc_date


def hires_to_go(start_date: date, end_date: date | None = None) -> tuple[FieldFilter, ...]:
    fils = (
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.CANCELLED),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
        FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
        FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.AFTER, value=to_cmc_date(start_date)),
    )
    if end_date:
        fils += (
            FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.BEFORE, value=to_cmc_date(end_date)),
        )
    return fils


@functools.lru_cache
def initial_filter(filtername: str) -> FilterArray:
    hire_start = date.today() - timedelta(days=300)
    hire_end = date.today() + timedelta(days=300)
    sale_start = date.today() - timedelta(days=490)

    match filtername:
        case 'Hire':
            fils = hires_to_go(hire_start, hire_end)
            logic = None
            sorts = ((HireAliases.SEND_DATE, SortOrder.DESC),)

        case 'Sale':
            fils = sales_fils(sale_start)
            logic = None
            sorts = ((SaleAliases.DATE_ORDERED, SortOrder.DESC),)

        case 'Customer':
            fils = customer_fils(hire_start, sale_start)
            logic = 'Or, And, And'
            sorts = None

        case _:
            raise ValueError(f'No filter for {filtername}')

    res = FilterArray.from_filters(*fils, sorts=sorts, logic=logic)
    return res


def sales_fils(sale_start):
    return (
        FieldFilter(
            column=SaleAliases.DATE_ORDERED,
            condition=ConditionType.AFTER,
            value=to_cmc_date(sale_start)
        ),)


def customer_fils(hire_start, sale_start):
    return (
        ConnectedFieldFilter.model_validate(
            dict(
                column='Has Hired',
                connection_category='Hire',
                connected_column=HireAliases.SEND_DATE,
                condition=ConditionType.AFTER,
                value=to_cmc_date(hire_start),
            )
        ),
        ConnectedFieldFilter.model_validate(
            dict(
                column='Involves',
                connection_category='Sale',
                connected_column=SaleAliases.DATE_ORDERED,
                condition=ConditionType.AFTER,
                value=to_cmc_date(sale_start),
            )
        ),
    )
