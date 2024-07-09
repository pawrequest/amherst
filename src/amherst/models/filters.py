from __future__ import annotations

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

FilterName = Literal['initial']

HIRE_START_DATE = date.today() - timedelta(days=30)
HIRE_END_DATE = date.today() + timedelta(days=30)
HIRE_FILS = (
    FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.AFTER, value=to_cmc_date(HIRE_START_DATE)),
    FieldFilter(column=HireAliases.SEND_DATE, condition=ConditionType.BEFORE, value=to_cmc_date(HIRE_END_DATE)),
    FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_OK),
    FieldFilter(column=HireAliases.STATUS, condition=ConditionType.NOT_EQUAL, value=HireStatus.RTN_PROBLEMS),
)
HIRE_SORTS = ((HireAliases.SEND_DATE, SortOrder.DESC),)

HIRE_FILTER_ARRAY = FilterArray.from_filters(
    *HIRE_FILS,
    sorts=HIRE_SORTS
)


SALE_START_DATE = date.today() - timedelta(days=30)
SALE_FILTERS = (
    FieldFilter(column=SaleAliases.DATE_ORDERED, condition=ConditionType.AFTER, value=to_cmc_date(SALE_START_DATE)),
)
SALE_SORTS = ((SaleAliases.DATE_ORDERED, SortOrder.DESC),)

SALE_FILTER_ARRAY = FilterArray.from_filters(
    *SALE_FILTERS,
    sorts=SALE_SORTS
)


CUSTOMER_HIRE_CONNECTION = Connection2(name='Has Hired', category='Hire', column='Name')
CUSTOMER_SALE_CONNECTION = Connection2(name='Involves', category='Sale', column='Name')
CUSTOMER_HIRE_FILTERS = [ConnectedFieldFilter.from_field_fil(f, CUSTOMER_HIRE_CONNECTION) for f in HIRE_FILS]
CUSTOMER_SALE_FILTERS = [ConnectedFieldFilter.from_field_fil(f, CUSTOMER_SALE_CONNECTION) for f in SALE_FILTERS]
CUSTOMER_SORTS = None

CUSTOMER_FILTER_ARRAY = FilterArray.from_filters(
    *CUSTOMER_HIRE_FILTERS,
    *CUSTOMER_SALE_FILTERS,
    logics=['And', 'And', 'And', 'Or'],
    sorts=CUSTOMER_SORTS,
)
