from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import date
from typing import Any

from shipaw.fapi.responses import ShipmentResponse
from shipaw.models.ship_types import ShipDirection

from amherst.models.amherst_models import (
    AmherstHire,
    AmherstShipableBase,
)
from amherst.models.shipment import AmherstShipment

from .amherst_models import join_csv

CmcUpdateFuncAgnost = Callable[[AmherstShipableBase, AmherstShipment, ShipmentResponse], Awaitable[dict[str, str]]]


async def make_update_dict(shipment: AmherstShipment, shipment_response: ShipmentResponse) -> dict[str, Any]:
    """Adds tracking numbers and link."""
    record = shipment.record
    update_package = await _cmc_update_dict_base(shipment, shipment_response)
    if isinstance(record, AmherstHire):
        extra = await _cmc_update_dict_hire_extras(shipment)
        update_package.update(extra)
    return update_package


async def _cmc_update_dict_base(shipment: AmherstShipment, shipment_response: ShipmentResponse):
    record = shipment.record
    shipdir = shipment.direction
    new_tracking_links = shipment_response.tracking_links
    new_tracking_numbers = shipment_response.shipment_numbers
    nums_field = record.alias_lookup('tracking_numbers')
    tracking_numbers = record.tracking_numbers
    tracking_numbers.extend(new_tracking_numbers)

    if shipdir in [ShipDirection.INBOUND, ShipDirection.DROPOFF]:
        links_field = record.alias_lookup('tracking_links_in')
        old_links = record.tracking_links_in

    elif shipdir == ShipDirection.OUTBOUND:
        links_field = record.alias_lookup('tracking_links_out')
        old_links = record.tracking_links_out

    else:
        raise ValueError(f'Invalid shipment direction: {shipdir}')

    old_links.extend(new_tracking_links)

    update_package = {
        links_field: join_csv(old_links),
        nums_field: join_csv(tracking_numbers),
    }
    return update_package


async def _cmc_update_dict_hire_extras(shipment: AmherstShipment) -> dict:
    record = shipment.record
    if not isinstance(record, AmherstHire):
        raise ValueError('Record is not an AmherstHire')
    shipdir = shipment.direction
    if shipdir in [ShipDirection.INBOUND, ShipDirection.DROPOFF]:
        return await _extras_hire_in(record, shipment)
    elif shipdir == ShipDirection.OUTBOUND:
        return await _extras_hire_out(record)
    else:
        raise ValueError(f'Invalid shipment direction: {shipdir}')


async def _extras_hire_in(record: AmherstHire, shipment: AmherstShipment) -> dict:
    ret_notes = f'{date.today().strftime("%d/%m")}: pickup arranged for {shipment.shipping_date.strftime("%d/%m")}\r\n{record.return_notes}'
    return {
        record.alias_lookup('arranged_in'): 'True',
        record.alias_lookup('pickup_date'): f'{shipment.shipping_date:%Y-%m-%d}',
        record.alias_lookup('return_notes'): ret_notes,
    }


async def _extras_hire_out(record: AmherstHire) -> dict:
    return {
        record.alias_lookup('arranged_out'): 'True',
    }
