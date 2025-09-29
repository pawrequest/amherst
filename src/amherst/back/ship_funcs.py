from __future__ import annotations

import json

from httpx import HTTPStatusError
from loguru import logger
from pycommence import pycommence_context

from amherst.models.amherst_models import AmherstShipableBase
from amherst.models.shipment import AmherstShipment
from amherst.models.cmc_update import make_update_dict
from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.alerts import Alert, AlertType
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.shipment import Shipment as ShipmentAgnost
from parcelforce_expresslink.client import ParcelforceClient

from amherst.models.maps import AmherstMap, mapper_from_query_csrname


def extract_http_error_message(exception: HTTPStatusError) -> str:
    if hasattr(exception, 'response') and exception.response is not None:
        return exception.response.text
    logger.warning('HTTPStatusError has no response attribute')
    return str(exception)


def extract_http_error_message_json(exception: HTTPStatusError) -> dict:
    error_string = extract_http_error_message(exception)
    try:
        error_data = json.loads(error_string)
        return error_data.get('Messages')

    except json.JSONDecodeError:
        logger.warning('Error.response.text is not valid JSON')
        return {'Code': error_string, 'Description': ''}


async def http_status_alerts(exception: HTTPStatusError) -> list[Alert]:
    error_dict = extract_http_error_message_json(exception)
    return [Alert(message=f'{error_dict.get('Code')}:  {error_dict.get('Description')}', type=AlertType.ERROR)]


async def try_book_shipment(shipment_request: ShipmentRequest) -> ShipmentBookingResponse:
    shipment_response = ShipmentBookingResponse(shipment=shipment_request.shipment)
    try:
        shipment_response = shipment_request.provider.book_shipment(shipment_request.shipment)
        logger.info(f'Booked Shipment Response: {shipment_response.shipment_num}')

    except HTTPStatusError as e:
        for alert in await http_status_alerts(e):
            shipment_response.alerts += alert

    except Exception as e:
        logger.exception(f'Error booking shipment: {e}')
        shipment_response.alerts += Alert.from_exception(e)

    return shipment_response


async def try_update_cmc(
    record: AmherstShipableBase, shipment: AmherstShipment, shipment_response: ShipmentBookingResponse
):
    try:
        update_dict = await make_update_dict(record, shipment, shipment_response)
        logger.info(f'Updating CMC: {update_dict}')
        with pycommence_context(csrname=shipment.row_info.category) as pycmc1:
            pycmc1.update_row(update_dict, row_id=shipment.row_info.id)

    except ValueError as e:
        msg = f'Error updating Commence: {e}'
        logger.exception(e)
        shipment_response.alerts += Alert(message=msg, type=AlertType.ERROR)


def get_el_client() -> ParcelforceClient:
    try:
        return ParcelforceClient()
    except Exception as e:
        logger.error(f'Error getting Parcelforce ExpressLink Client: {e}')
        raise
