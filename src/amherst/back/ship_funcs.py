from __future__ import annotations

from loguru import logger
from pycommence import pycommence_context

from amherst.models.maps import AmherstMap, mapper_from_query_csrname
from shipaw.agnostic.requests import ShipmentRequestAgnost
from shipaw.agnostic.responses import Alert, AlertType, ShipmentBookingResponseAgnost
from shipaw.agnostic.shipment import Shipment as ShipmentAgnost
from shipaw.parcelforce.client import ParcelforceClient


async def try_book_shipment(shipment_request: ShipmentRequestAgnost) -> ShipmentBookingResponseAgnost:
    shipment_response = ShipmentBookingResponseAgnost(shipment=shipment_request.shipment)
    try:
        shipment_response = shipment_request.provider.book_shipment(shipment_request.shipment)
        logger.info(f'Booked Shipment Response: {shipment_response.shipment_num}')

    except Exception as e:
        logger.exception(f'Error booking shipment: {e}')
        shipment_response.alerts += Alert.from_exception(e)
    return shipment_response


async def try_update_cmc(record, shipment: ShipmentAgnost, shipment_response: ShipmentBookingResponseAgnost):
    try:
        mapper: AmherstMap = await mapper_from_query_csrname(record.row_info.category)
        if mapper.cmc_update_fn:
            update_dict = await mapper.cmc_update_fn(record, shipment, shipment_response)
            logger.info(f'Updating CMC: {update_dict}')
            with pycommence_context(csrname=record.row_info.category) as pycmc1:
                pycmc1.update_row(update_dict, row_id=record.row_info.id)

        else:
            logger.warning('NO CMC UPDATE FUNCTION')

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
