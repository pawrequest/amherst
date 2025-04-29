from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum
from typing import NamedTuple

from fastapi import Query

from amherst.models.amherst_models import (
    AMHERST_SHIPMENT_TYPES,
    AMHERST_TABLE_MODELS,
    AmherstCustomer,
    AmherstHire,
    AmherstSale,
    AmherstShipmentOut,
    AmherstShipmentResponse,
    AmherstTableBase,
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


CMC_UPDATE_FN = Callable[[AmherstShipmentOut, AmherstShipmentResponse], dict[str, str]]
CMC_UPDATE_FN2 = Callable[[AMHERST_TABLE_MODELS, AMHERST_SHIPMENT_TYPES, AmherstShipmentResponse], dict[str, str]]


def update_trial_2(
    record: AmherstTrial, shipment: AMHERST_SHIPMENT_TYPES, resp: AmherstShipmentResponse
) -> dict[str, str]:
    tracking_link = resp.tracking_link()
    if record.tracking_numbers:
        shipment_ids = record.tracking_numbers.split(',')
        shipment_ids.append(resp.shipment_num)
        shipment_ids_str = ', '.join(shipment_ids)
    else:
        shipment_ids_str = resp.shipment_num
    update_dict = {TrialAliases.TRACKING_NUMBERS: shipment_ids_str}
    match shipment.direction:
        case 'out':
            update_dict.update({TrialAliases.TRACK_OUT: tracking_link})
        case ['in', 'dropoff']:
            update_dict.update({TrialAliases.TRACK_IN: tracking_link})
        case _:
            raise ValueError
    return update_dict


def update_hire_shipment(shipment: AmherstShipmentOut, shipment_response: AmherstShipmentResponse):
    tracking_link = shipment_response.tracking_link()
    match shipment.direction:
        case ['in', 'dropoff']:
            return {
                HireAliases.TRACK_IN: tracking_link,
                HireAliases.ARRANGED_IN: True,
                HireAliases.PICKUP_DATE: f'{shipment.shipping_date:%Y-%m-%d}',
            }
        case 'out':
            return {HireAliases.TRACK_OUT: tracking_link, HireAliases.ARRANGED_OUT: True}
        case _:
            raise ValueError


# def update_shipment(record: AmherstTableBase, shipment: AmherstShipmentOut, shipment_response: AmherstShipmentResponse):
#     tracking_link = shipment_response.tracking_link()
#     update_package = {
#         HireAliases.TRACKING_NUMBERS: f'{record.tracking_numbers}, {shipment_response.shipment_num}',
#     }
#     if shipment.direction in ['in', 'dropoff']:
#         update_package.update(
#             {
#                 HireAliases.TRACK_IN: tracking_link,
#                 HireAliases.ARRANGED_IN: True,
#                 HireAliases.PICKUP_DATE: f'{shipment.shipping_date:%Y-%m-%d}',
#             }
#         )
#     else:
#         update_package.update({HireAliases.TRACK_OUT: tracking_link, HireAliases.ARRANGED_OUT: True})
#     return update_package


# def update_hire_shipment2(hire: AmherstHire, shipment: AmherstShipmentOut, shipment_response: AmherstShipmentResponse):
#     tracking_link = shipment_response.tracking_link()
#     update_package = {
#         HireAliases.TRACKING_NUMBERS: f'{hire.tracking_numbers}, {shipment_response.shipment_num}',
#     }
#     if shipment.direction in ['in', 'dropoff']:
#         update_package.update(
#             {
#                 HireAliases.TRACK_IN: tracking_link,
#                 HireAliases.ARRANGED_IN: True,
#                 HireAliases.PICKUP_DATE: f'{shipment.shipping_date:%Y-%m-%d}',
#             }
#         )
#     else:
#         update_package.update({HireAliases.TRACK_OUT: tracking_link, HireAliases.ARRANGED_OUT: True})
#     return update_package


def update_sale_shipment2(sale: AmherstSale, shipment: AmherstShipmentOut, shipment_response: AmherstShipmentResponse):
    tracking_link = shipment_response.tracking_link()
    update_package = {
        SaleAliases.TRACKING_NUMBERS: f'{sale.tracking_numbers}, {shipment_response.shipment_num}',
        SaleAliases.TRACK_OUT: tracking_link,
        SaleAliases.ARRANGED_OUT: True,
    }
    return update_package


def update_customer_shipment2(
    customer: AmherstCustomer, shipment: AmherstShipmentOut, shipment_response: AmherstShipmentResponse
):
    tracking_link = shipment_response.tracking_link()
    update_package = {
        CustomerAliases.TRACKING_NUMBERS: f'{customer.tracking_numbers}, {shipment_response.shipment_num}',
        CustomerAliases.TRACK_OUT: tracking_link,
    }
    return update_package


def update_sale_shipment(shipment: AmherstShipmentOut, shipment_response: AmherstShipmentResponse):
    tracking_link = shipment_response.tracking_link()
    return {
        SaleAliases.TRACK_OUT: tracking_link,
        SaleAliases.ARRANGED_OUT: True,
    }


def update_trial_shipment(): ...


class AmherstMap(NamedTuple):
    category: CategoryName
    record_model: type(AmherstTableBase)
    aliases: type(StrEnum)
    templates: TemplateMap
    cmc_update_fn: CMC_UPDATE_FN | None = None
    cmc_update_fn2: CMC_UPDATE_FN2 | None = None
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
        cmc_update_fn=update_hire_shipment,
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
        cmc_update_fn=update_sale_shipment,
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
    )

    trial: AmherstMap = AmherstMap(
        category=CategoryName.Trial,
        record_model=AmherstTrial,
        aliases=TrialAliases,
        templates=TemplateMap(
            listing='customer_list.html',
            detail='customer_detail.html',
        ),
        cmc_update_fn2=update_trial_2
        # connections=ConnectionMap(
        #     hire=HIRE_CONNECTION,
        #     sale=SALE_CONNECTION,
        # ),
        # py_filters=FilterMapPy(
        #     loose=customer_row_filter_loose,
        #     tight=customer_row_filter_loose,
        # ),
        # cmc_filters=FilterMapCmc(
        #     loose=CUSTOMER_ARRAY_LOOSE,
        #     tight=CUSTOMER_ARRAY_TIGHT,
        # ),
    )


async def maps2(csrname: CategoryName = Query(...)) -> AmherstMap:
    return getattr(AmherstMaps, csrname.name.lower())
