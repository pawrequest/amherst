from __future__ import annotations

from enum import StrEnum
from typing import NamedTuple

from fastapi import Query

from amherst.models.amherst_models import AmherstCustomer, AmherstHire, AmherstSale, AmherstTableBase, AmherstTrial
from amherst.models.commence_adaptors import AmherstTableName, CustomerAliases, HireAliases, SaleAliases, TrialAliases
from amherst.models.filters import (
    CUSOMER_CONNECTION,
    CUSTOMER_ARRAY_LOOSE,
    CUSTOMER_ARRAY_TIGHT,
    HIRE_ARRAY_TIGHT,
    SALE_ARRAY_TIGHT,
    customer_row_filter,
    hire_row_filter,
    sale_row_filter,
)
from pycommence.filters import FilterArray
from pycommence.pycmc_types import Connection, RowFilter


class FilterMapRow(NamedTuple):
    loose: RowFilter | None = None
    tight: RowFilter | None = None


class FilterMapArray(NamedTuple):
    loose: FilterArray | None = None
    tight: FilterArray | None = None


HireArrayMap = FilterMapArray(
    loose=HIRE_ARRAY_TIGHT,
    tight=HIRE_ARRAY_TIGHT,
)

SaleArrayMap = FilterMapArray(
    loose=SALE_ARRAY_TIGHT,
    tight=SALE_ARRAY_TIGHT,
)

CustomerArrayMap = FilterMapArray(
    loose=CUSTOMER_ARRAY_LOOSE,
    tight=CUSTOMER_ARRAY_TIGHT,
)


HireFilterMap = FilterMapRow(
    loose=hire_row_filter,
    tight=hire_row_filter,
)

SaleFilterMap = FilterMapRow(
    loose=sale_row_filter,
    tight=sale_row_filter,
)

CustomerFilterMap = FilterMapRow(
    loose=customer_row_filter,
    tight=customer_row_filter,
)


class AmherstMapping(NamedTuple):
    category: AmherstTableName
    record_model: type(AmherstTableBase)
    aliases: type(StrEnum)
    listing_template: str = 'customers.html'
    detail_template: str = 'hires_sales.html'
    default_filter: FilterArray = FilterArray()
    customer_connection: Connection | None = None
    filter_map_row: FilterMapRow | None = None
    filter_map_array: FilterMapArray | None = None


Hire_Map = AmherstMapping(
    category=AmherstTableName.Hire,
    record_model=AmherstHire,
    aliases=HireAliases,
    default_filter=HIRE_ARRAY_TIGHT,
    customer_connection=CUSOMER_CONNECTION,
    filter_map_row=HireFilterMap,
    filter_map_array=HireArrayMap,
)


class AmherstMaps:
    hire: AmherstMapping = AmherstMapping(
        category=AmherstTableName.Hire,
        record_model=AmherstHire,
        aliases=HireAliases,
        default_filter=HIRE_ARRAY_TIGHT,
        customer_connection=CUSOMER_CONNECTION,
        filter_map_row=HireFilterMap,
        filter_map_array=HireArrayMap,
    )
    sale: AmherstMapping = AmherstMapping(
        category=AmherstTableName.Sale,
        record_model=AmherstSale,
        aliases=SaleAliases,
        default_filter=SALE_ARRAY_TIGHT,
        customer_connection=CUSOMER_CONNECTION,
        filter_map_row=SaleFilterMap,
        filter_map_array=SaleArrayMap,
    )
    customer: AmherstMapping = AmherstMapping(
        category=AmherstTableName.Customer,
        record_model=AmherstCustomer,
        aliases=CustomerAliases,
        default_filter=CUSTOMER_ARRAY_TIGHT,
        listing_template='customers.html',
        filter_map_row=CustomerFilterMap,
        filter_map_array=CustomerArrayMap,
    )


async def maps2(csrname: AmherstTableName = Query(...)) -> AmherstMapping:
    return getattr(AmherstMaps, csrname.lower())


Sale_Map = AmherstMapping(
    category=AmherstTableName.Sale,
    record_model=AmherstSale,
    aliases=SaleAliases,
    default_filter=SALE_ARRAY_TIGHT,
    customer_connection=CUSOMER_CONNECTION,
    filter_map_row=SaleFilterMap,
    filter_map_array=SaleArrayMap,
)

Customer_Map = AmherstMapping(
    category=AmherstTableName.Customer,
    record_model=AmherstCustomer,
    aliases=CustomerAliases,
    default_filter=CUSTOMER_ARRAY_TIGHT,
    listing_template='customers.html',
    filter_map_row=CustomerFilterMap,
    filter_map_array=CustomerArrayMap,
)

Trial_Map = AmherstMapping(
    category=AmherstTableName.Trial,
    record_model=AmherstTrial,
    aliases=TrialAliases,
)

MODEL_MAPS = {
    AmherstTableName.Hire: Hire_Map,
    AmherstTableName.Sale: Sale_Map,
    AmherstTableName.Customer: Customer_Map,
    AmherstTableName.Trial: Trial_Map,
}


def model_maps():
    return {
        AmherstTableName.Hire: Hire_Map,
        AmherstTableName.Sale: Sale_Map,
        AmherstTableName.Customer: Customer_Map,
        AmherstTableName.Trial: Trial_Map,
    }


async def mapper_csrname(csrname: AmherstTableName = Query(...)) -> AmherstMapping:
    return MODEL_MAPS[csrname]
