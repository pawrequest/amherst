from __future__ import annotations

import pathlib
import time

from loguru import logger
from pawdf.array_pdf.array_p import on_a4
from pycommence import pycommence_context
from shipaw.agnostic.agnost import Shipment
from shipaw.parcelforce.msg import Alerts, ShipmentResponse

from amherst.models.maps import mapper_from_query_csrname, AmherstMap


def book_shipment(el_client, shipment: Shipment) -> ShipmentResponse:
    resp: ShipmentResponse = el_client.request_shipment(shipment)
    logger.debug(f'Booking response: {resp.status=}, {resp.success=}')
    return resp


async def try_book_shipment(el_client, shipment_proposed) -> tuple[ShipmentResponse | None, Alerts]:
    alerts = Alerts.empty()
    shipment_response: ShipmentResponse | None = None
    try:
        shipment_response: ShipmentResponse = book_shipment(el_client, shipment_proposed)
        logger.info(f'Booked Shipment Response: {shipment_response}')
        alerts += shipment_response.alerts

    except Exception as e:
        logger.error(f'Error booking shipment: {e}')
        alerts += Alert.from_exception(e)
    return shipment_response, alerts


async def maybe_get_label(el_client, shipment_proposed: Shipment, shipment_response):
    if (
        shipment_proposed.direction in [ShipDirection.DROPOFF, ShipDirection.OUTBOUND]
        or shipment_proposed.print_own_label
    ):
        unsize = shipment_proposed.label_file.parent / 'original_size' / shipment_proposed.label_file.name
        unsize.parent.mkdir(parents=True, exist_ok=True)
        wait_label(shipment_num=shipment_response.shipment_num, dl_path=unsize, el_client=el_client)
        on_a4(input_file=unsize, output_file=shipment_proposed.label_file)
    else:
        logger.warning('No label Requested')


async def try_update_cmc(record, shipment_proposed, shipment_response):
    try:
        mapper: AmherstMap = await mapper_from_query_csrname(record.row_info.category)
        if mapper.cmc_update_fn:
            update_dict = await mapper.cmc_update_fn(record, shipment_proposed, shipment_response)
            logger.info(f'Updating CMC: {update_dict}')
            with pycommence_context(csrname=record.row_info.category) as pycmc1:
                pycmc1.update_row(update_dict, row_id=record.row_info.id)

        else:
            logger.warning('NO CMC UPDATE FUNCTION')

    except ValueError as e:
        msg = f'Error updating Commence: {e}'
        logger.exception(e)
        shipment_response.alerts += Alert(message=msg, type=AlertType.ERROR)



def get_el_client() -> ELClient:
    try:
        return ELClient()
    except Exception as e:
        logger.error(f'Error getting Parcelforce ExpressLink Client: {e}')
        raise
