from __future__ import annotations

from datetime import date
from typing import Any, cast

from loguru import logger
from pycommence import pycommence_context
from shipaw.fapi.alerts import Alert, AlertType
from shipaw.fapi.responses import ShipmentResponse
from shipaw.utils.consts_enums import ShipDirection

from amherst.models.amherst_models import AmherstHire
from amherst.models.commence_adaptors import CategoryName
from amherst.models.commence_shipment import CommenceShipment
from amherst.models.shipment import AmherstShipment, AmherstShipmentRequest


async def safe_call(func, *args, response, error_msg):
    try:
        await func(*args)
    except Exception as e:
        msg = f'{error_msg}: {e}'
        logger.exception(e)
        response.alerts += Alert(message=msg, type=AlertType.ERROR)


async def cmc_callback(request: AmherstShipmentRequest, response: ShipmentResponse):
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
        with pycommence_context(csrname=shipment.row_info.category) as pycmc1:
            pycmc1.update_row(update_dict, row_id=shipment.row_info.id)


async def make_update_dict(shipment: AmherstShipment) -> dict[str, Any]:
    record = shipment.record
    if isinstance(record, AmherstHire):
        record = cast(AmherstHire, record)
        return await _cmc_update_dict_hire(record, shipment.direction, shipment.shipping_date)
    return {}


async def _cmc_update_dict_hire(record: AmherstHire, direction: ShipDirection, shipping_date: date) -> dict:
    match direction:
        case ShipDirection.OUTBOUND:
            return {AmherstHire.alias_lookup('arranged_out'): 'True'}
        case ShipDirection.INBOUND | ShipDirection.DROPOFF:
            ret_notes = (
                f'{date.today().strftime("%d/%m")}: pickup arranged for'
                f' {shipping_date.strftime("%d/%m")}\r\n{record.return_notes}'
            )
            return {
                AmherstHire.alias_lookup('arranged_in'): 'True',
                AmherstHire.alias_lookup('pickup_date'): f'{shipping_date:%Y-%m-%d}',
                AmherstHire.alias_lookup('return_notes'): ret_notes,
            }
        case _:
            raise ValueError(f'Invalid shipment direction: {direction}')


async def cmc_shipment_obj(shipment: AmherstShipment, shipment_response: ShipmentResponse) -> CommenceShipment:
    record = shipment.record
    res = CommenceShipment(
        label=str(shipment_response.label_path),
        direction=shipment.direction,
        customer=[record.customer_name],
        tracking_links=shipment_response.tracking_links,
        latest_tracking=shipment_response.tracking_links[0] if shipment_response.tracking_links else None,
    )
    if record.category.lower() in ['hire', 'sale']:
        setattr(res, record.category.lower(), [record.name])
    return res


async def create_shipment_in_cmc(shipment: AmherstShipment, shipment_response: ShipmentResponse):
    shipment_obj = await cmc_shipment_obj(shipment, shipment_response)
    ship_dict = shipment_obj.model_dump(by_alias=True)
    with pycommence_context(csrname=CategoryName.Shipment) as pycmc:
        pycmc.create_row(ship_dict, csrname=CategoryName.Shipment)
