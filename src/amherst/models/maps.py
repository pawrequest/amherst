from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from typing import Any, Awaitable, NamedTuple

from fastapi import Query
from shipaw.ship_types import ShipDirection

from amherst.models.amherst_models import (
    AMHERST_SHIPMENT_TYPES,
    AMHERST_TABLE_MODELS,
    AmherstCustomer,
    AmherstHire,
    AmherstSale,
    AmherstShipmentOut,
    AmherstShipmentResponse,
    AmherstShipableBase,
    AmherstTrial,
)
from amherst.models.commence_adaptors import CategoryName, CustomerAliases, HireAliases, SaleAliases, TrialAliases
from amherst.models.filters import (
    CUSOMER_CONNECTION,
    CUSTOMER_ARRAY_LOOSE,
    CUSTOMER_ARRAY_TIGHT,
    HIRE_ARRAY_LOOSE,
    HIRE_ARRAY_TIGHT,
    HIRE_CONNECTION,
    SALE_ARRAY_LOOSE,
    SALE_ARRAY_TIGHT,
    SALE_CONNECTION,
    customer_row_filter_loose,
    hire_row_filter_loose,
    sale_row_filter_loose,
)
from pycommence.filters import FilterArray
from pycommence.pycmc_types import Connection, RowFilter


class FilterMapPy(NamedTuple):
    loose: RowFilter | None = None
    tight: RowFilter | None = None


class FilterMapCmc(NamedTuple):
    loose: FilterArray | None = None
    tight: FilterArray | None = None


class ConnectionMap(NamedTuple):
    customer: Connection | None = None
    hire: Connection | None = None
    sale: Connection | None = None


class TemplateMap(NamedTuple):
    listing: str
    detail: str


CmcUpdateFunc = Callable[
    [AMHERST_TABLE_MODELS, AMHERST_SHIPMENT_TYPES, AmherstShipmentResponse], Awaitable[dict[str, str]]
]


async def get_alias(record) -> type(StrEnum):
    mapper = await mapper_from_query_csrname(record.category)
    aliases = mapper.aliases
    return aliases


async def get_track_dir_field(aliases, shipment) -> str:
    if shipment.direction == ShipDirection.OUTBOUND:
        return aliases.TRACK_OUT
    elif shipment.direction in [ShipDirection.INBOUND, ShipDirection.DROPOFF]:
        return aliases.TRACK_IN
    else:
        raise ValueError('Invalid shipment direction')


def split_com_sep_str_field(record, fieldname: str) -> list[str]:
    data_s: str = getattr(record, fieldname, None)
    data_l = data_s.split(',') if data_s else []
    return data_l


def add_to_com_sep_str_field(data: list, value) -> str:
    data.append(value)
    return ','.join(data)


async def add_tracking_to_list(record: AMHERST_TABLE_MODELS, resp) -> str:
    tracks = split_com_sep_str_field(record, 'tracking_numbers')
    return add_to_com_sep_str_field(tracks, resp.shipment_num)


async def make_base_update_dict(
    record: AMHERST_TABLE_MODELS, shipment: AMHERST_SHIPMENT_TYPES, shipment_response: AmherstShipmentResponse
) -> dict[str, Any]:
    """Adds tracking numbers and link."""
    aliases = await get_alias(record)
    tracks = await add_tracking_to_list(record, shipment_response)
    update_package = {aliases.TRACKING_NUMBERS: tracks}
    return update_package


async def make_hire_update_dict(
    record: AmherstHire, shipment: AmherstShipmentOut, shipment_response: AmherstShipmentResponse
):
    aliases = await get_alias(record)
    update_base = await make_base_update_dict(record, shipment, shipment_response)
    shipdir = shipment.direction
    if shipdir in [ShipDirection.INBOUND, ShipDirection.DROPOFF]:
        extra = {aliases.ARRANGED_IN: 'True', HireAliases.PICKUP_DATE: f'{shipment.shipping_date:%Y-%m-%d}'}
    elif shipdir == ShipDirection.OUTBOUND:
        extra = {aliases.ARRANGED_OUT: 'True'}
    else:
        raise ValueError(f'Invalid shipment direction: {shipdir}')
    extra.update(update_base)
    return extra


class AmherstMap(NamedTuple):
    category: CategoryName
    record_model: type(AmherstShipableBase)
    aliases: type(StrEnum)
    templates: TemplateMap
    cmc_update_fn: CmcUpdateFunc | None = None
    connections: ConnectionMap | None = None
    py_filters: FilterMapPy | None = None
    cmc_filters: FilterMapCmc | None = None


class AmherstMaps:
    hire: AmherstMap = AmherstMap(
        category=CategoryName.Hire,
        record_model=AmherstHire,
        aliases=HireAliases,
        templates=TemplateMap(
            listing='order_list.html',
            detail='order_detail.html',
        ),
        connections=ConnectionMap(
            customer=CUSOMER_CONNECTION,
        ),
        py_filters=FilterMapPy(
            loose=hire_row_filter_loose,
            tight=hire_row_filter_loose,
        ),
        cmc_filters=FilterMapCmc(
            loose=HIRE_ARRAY_LOOSE,
            tight=HIRE_ARRAY_TIGHT,
        ),
        cmc_update_fn=make_hire_update_dict,
    )
    sale: AmherstMap = AmherstMap(
        category=CategoryName.Sale,
        record_model=AmherstSale,
        aliases=SaleAliases,
        templates=TemplateMap(
            listing='order_list.html',
            detail='order_detail.html',
        ),
        connections=ConnectionMap(
            customer=CUSOMER_CONNECTION,
        ),
        py_filters=FilterMapPy(
            loose=sale_row_filter_loose,
            tight=sale_row_filter_loose,
        ),
        cmc_filters=FilterMapCmc(
            loose=SALE_ARRAY_LOOSE,
            tight=SALE_ARRAY_TIGHT,
        ),
        cmc_update_fn=make_base_update_dict,
    )
    customer: AmherstMap = AmherstMap(
        category=CategoryName.Customer,
        record_model=AmherstCustomer,
        aliases=CustomerAliases,
        templates=TemplateMap(
            listing='customer_list.html',
            detail='customer_detail.html',
        ),
        connections=ConnectionMap(
            hire=HIRE_CONNECTION,
            sale=SALE_CONNECTION,
        ),
        py_filters=FilterMapPy(
            loose=customer_row_filter_loose,
            tight=customer_row_filter_loose,
        ),
        cmc_filters=FilterMapCmc(
            loose=CUSTOMER_ARRAY_LOOSE,
            tight=CUSTOMER_ARRAY_TIGHT,
        ),
        cmc_update_fn=make_base_update_dict,
    )

    trial: AmherstMap = AmherstMap(
        category=CategoryName.Trial,
        record_model=AmherstTrial,
        aliases=TrialAliases,
        templates=TemplateMap(
            listing='customer_list.html',
            detail='customer_detail.html',
        ),
        cmc_update_fn=make_base_update_dict,
    )


async def mapper_from_query_csrname(csrname: CategoryName = Query(...)) -> AmherstMap:
    return getattr(AmherstMaps, csrname.lower())

