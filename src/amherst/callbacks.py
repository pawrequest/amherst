from __future__ import annotations

from datetime import date
from typing import Any, cast

from amherst_core.models import AmherstCustomer, AmherstHire, AmherstOrderBase
from loguru import logger
from pycommence import PyCommence
from shipaw.fapi.alerts import Alert, AlertType
from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipmentResponse
from shipaw.utils.consts_enums import ShipDirection

from amherst.models.amherst_base import alias_lookup
from amherst.models.commence_adaptors import CategoryName
from amherst.models.commence_shipment import CommenceShipment, ordinal_date_name
from amherst.models.shipment import AmherstShipment, AmherstShipmentRequest


async def safe_call(func, *args, response, error_msg):
    try:
        await func(*args)
    except Exception as e:
        msg = f'{error_msg}: {e}'
        logger.exception(e)
        response.alerts += Alert(message=msg, type=AlertType.ERROR)


async def cmc_callback(request: ShipmentRequest, response: ShipmentResponse):
    request = AmherstShipmentRequest.model_validate(request, from_attributes=True)
    shipment = request.shipment
    await safe_call(update_cmc, shipment, response=response, error_msg='Error updating Commence')
    await safe_call(
        create_shipment_in_cmc, shipment, response, response=response, error_msg='Error creating Commence Shipment'
    )
    logger.info(
        f'Updated Commence row id {shipment.row_info.id} in {shipment.row_info.category} Table\n'
        f'Added Shipment and connected to {request.shipment.record.category} record in Commence'
    )


async def update_cmc(shipment: AmherstShipment):
    if update_dict := await make_update_dict(shipment):
        logger.info(f'Updating CMC: {update_dict}')
        with PyCommence(shipment.row_info.category) as pycmc1:
            pycmc1.cursor().update_row(update_dict, id=shipment.row_info.id)


async def create_shipment_in_cmc(shipment: AmherstShipment, shipment_response: ShipmentResponse):
    shipment_obj = await cmc_shipment_obj(shipment, shipment_response)
    ship_dict = shipment_obj.model_dump(by_alias=True)
    with PyCommence(CategoryName.Shipment) as pycmc:
        pycmc.cursor().create_row(ship_dict)


async def make_update_dict(shipment: AmherstShipment) -> dict[str, Any]:
    record = shipment.record
    if isinstance(record, AmherstHire):
        record = cast(AmherstHire, record)
        return await _cmc_update_dict_hire(record, shipment.direction, shipment.shipping_date)
    return {}


async def _cmc_update_dict_hire(record: AmherstHire, direction: ShipDirection, shipping_date: date) -> dict:
    match direction:
        case ShipDirection.OUTBOUND:
            return {alias_lookup(AmherstHire, 'arranged_out'): 'True'}
        case ShipDirection.INBOUND | ShipDirection.DROPOFF:
            ret_notes = (
                f'{date.today().strftime("%d/%m")}: pickup arranged for'
                f' {shipping_date.strftime("%d/%m")}\r\n{record.return_notes}'
            )
            return {
                alias_lookup(AmherstHire, 'arranged_in'): 'True',
                alias_lookup(AmherstHire, 'pickup_date'): f'{shipping_date:%Y-%m-%d}',
                alias_lookup(AmherstHire, 'return_notes'): ret_notes,
            }
        case _:
            raise ValueError(f'Invalid shipment direction: {direction}')


async def cmc_shipment_obj(shipment: AmherstShipment, shipment_response: ShipmentResponse) -> CommenceShipment:
    record = shipment.record
    update = {
        'customers': [],
        'hires': [],
        'sales': [],
    }
    if isinstance(record, AmherstOrderBase):
        update['customers'] = record.customers
        order_type = record.category.lower() + 's'
        update[order_type] = [record.name]
    elif isinstance(record, AmherstCustomer):
        update['customers'] = [record.name]
    else:
        raise ValueError(f'Unsupported record type for shipment: {type(record)}')
    cmc_shipment = CommenceShipment(
        boxes=shipment.boxes,
        collection_id=shipment_response.collection_id or '',
        direction=shipment.direction,
        label=shipment_response.label_path,
        latest_tracking=shipment_response.tracking_links[0] if shipment_response.tracking_links else None,
        name=f'{ordinal_date_name()}',
        send_date=shipment.shipping_date,
        shipment_numbers=shipment_response.shipment_numbers,
        tracking_links=shipment_response.tracking_links,
        **update,
    )

    return cmc_shipment
