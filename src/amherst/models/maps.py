from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from typing import NamedTuple

from fastapi import Query

from amherst.models.amherst_models import AmherstCustomer, AmherstHire, AmherstSale, AmherstTableBase
from amherst.models.commence_adaptors import CsrName, CustomerAliases, HireAliases, SaleAliases
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
from shipaw.models.pf_msg import ShipmentResponse
from shipaw.models.pf_shipment import Shipment


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


CMC_UPDATE_FN = Callable[[Shipment, ShipmentResponse], dict[str, str]]


def hire_update_shipment(shipment: Shipment, shipment_response: ShipmentResponse):
    tracking_link = shipment_response.tracking_link()
    return (
        {
            HireAliases.TRACK_IN: tracking_link,
            HireAliases.ARRANGED_IN: True,
            HireAliases.PICKUP_DATE: f'{shipment.shipping_date:%Y-%m-%d}',
        }
        if shipment.direction in ['in', 'dropoff']
        else {HireAliases.TRACK_OUT: tracking_link, HireAliases.ARRANGED_OUT: True}
    )


class AmherstMap(NamedTuple):
    category: CsrName
    record_model: type(AmherstTableBase)
    aliases: type(StrEnum)
    templates: TemplateMap
    cmc_update_fn: CMC_UPDATE_FN | None = None
    connections: ConnectionMap | None = None
    py_filters: FilterMapPy | None = None
    cmc_filters: FilterMapCmc | None = None


class AmherstMaps:
    hire: AmherstMap = AmherstMap(
        category=CsrName.Hire,
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
        cmc_update_fn=hire_update_shipment,
    )
    sale: AmherstMap = AmherstMap(
        category=CsrName.Sale,
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
    )
    customer: AmherstMap = AmherstMap(
        category=CsrName.Customer,
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
    )


async def maps2(csrname: CsrName = Query(...)) -> AmherstMap:
    return getattr(AmherstMaps, csrname.lower())
