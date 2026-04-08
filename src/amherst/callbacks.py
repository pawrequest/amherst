from __future__ import annotations

from datetime import date
from typing import Any

from amherst_core.models import AmherstCustomer, AmherstHire, AmherstOrderBase
from amherst_core.models.shipment import CommenceShipmentAdd
from amherst_core.utils.get_set_convert import alias_lookup
from amherst_core.utils.text_and_date import dated_name
from loguru import logger
from pycommence import PyCommence
from pycommence.core.meta import CommenceTable
from shipaw.fapi.alerts import Alert, AlertType
from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.responses import ShipmentResponse
from shipaw.models.shipment import Shipment
from shipaw.utils.consts_enums import ShipDirection

from amherst.app_custom import AmherstRequest

# from amherst.models.amherst_base import alias_lookup


def safe_call(func, *args, response, error_msg, **kwargs):
    try:
        return func(*args, **kwargs)
    except Exception as e:
        msg = f'{error_msg}: {e}'
        logger.opt(depth=1).log(
            'ERROR',
            msg,
        )
        response.alerts += Alert(message=msg, type=AlertType.ERROR)


async def safe_call_async(func, *args, response, error_msg, **kwargs):
    return safe_call(func, *args, response=response, error_msg=error_msg, **kwargs)


async def cmc_callback(request: AmherstRequest, shipment_request: ShipmentRequest, response: ShipmentResponse):
    category = request.app.state.category
    row_id = request.app.state.row_id
    shipment = shipment_request.shipment

    with PyCommence(category, 'Shipment') as pycmc:
        row_data = pycmc.cursor(category).read_row(row_id=row_id)
        record = row_data.construct_model()
        update_dict = await make_update_dict(record, shipment)
        shipment_obj = new_cmc_shipment(record, shipment, response)
        ship_dict = shipment_obj.model_dump(by_alias=True)

        # update existing record
        record_updated = safe_call(
            pycmc.cursor(category).update_row,
            update_dict,
            row_id=row_id,
            response=response,
            error_msg='Error updating Commence',
        )
        # create and connect shipment record

        shipment_created = await safe_call_async(
            pycmc.cursor('Shipment').create_row,
            ship_dict,
            response=response,
            error_msg='Error creating Commence Shipment',
        )

    if shipment_created:
        logger.info(f'Created new Commence Shipment record and connected to {category} record')
    else:
        logger.error('Failed to create Commence Shipment record')
    if record_updated:
        logger.info(f'Updated Commence row id {record.name} in {category} Table')
    else:
        logger.error(f'Failed to update existing Commence record {record.name}')


async def make_update_dict(record: CommenceTable, shipment: Shipment) -> dict[str, Any]:
    if isinstance(record, AmherstHire):
        return await _cmc_update_dict_hire(record, shipment.direction, shipment.shipping_date)
    return {}  # create shipment so not many updates in sale etc


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


def new_cmc_shipment(
    record: CommenceTable, shipment: Shipment, shipment_response: ShipmentResponse
) -> CommenceShipmentAdd:
    record = record
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
    cmc_shipment = CommenceShipmentAdd(
        boxes=shipment.boxes,
        collection_id=shipment_response.collection_id or '',
        direction=shipment.direction,
        label=shipment_response.label_path,
        latest_tracking=shipment_response.tracking_links[0] if shipment_response.tracking_links else None,
        name=dated_name(
            record.customers[0] if isinstance(record, AmherstOrderBase) else record.name, shipment.shipping_date
        ),
        send_date=shipment.shipping_date,
        shipment_numbers=shipment_response.shipment_numbers,
        tracking_links=shipment_response.tracking_links,
        **update,
    )

    return cmc_shipment


async def new_cmc_shipment_async(
    record: CommenceTable, shipment: Shipment, shipment_response: ShipmentResponse
) -> CommenceShipmentAdd:
    return new_cmc_shipment(record, shipment, shipment_response)
