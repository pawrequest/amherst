from __future__ import annotations

import json
import pprint

from httpx import HTTPStatusError
from loguru import logger
from pycommence import pycommence_context

from amherst.models.amherst_models import AmherstShipableBase
from amherst.models.shipment import AmherstShipment, AmherstShipmentRequest
from amherst.models.cmc_update import make_update_dict
from shipaw.fapi.backend import http_status_alerts
from shipaw.fapi.requests import ShipmentRequest
from shipaw.fapi.alerts import Alert, AlertType
from shipaw.fapi.responses import ShipmentBookingResponse
from shipaw.models.shipment import Shipment as ShipmentAgnost
from parcelforce_expresslink.client import ParcelforceClient

from amherst.models.maps import AmherstMap, mapper_from_query_csrname


async def try_update_cmc(shipment: AmherstShipment, shipment_response: ShipmentBookingResponse
):
    try:
        update_dict = await make_update_dict(shipment, shipment_response)
        logger.info(f'Updating CMC: {update_dict}')
        with pycommence_context(csrname=shipment.row_info.category) as pycmc1:
            pycmc1.update_row(update_dict, row_id=shipment.row_info.id)
        logger.info(
            f'Updated Commence row id {shipment.row_info.id} in {shipment.row_info.category} with:\n{pprint.pformat(update_dict, indent=2)}'
        )

    except ValueError as e:
        msg = f'Error updating Commence: {e}'
        logger.exception(e)
        shipment_response.alerts += Alert(message=msg, type=AlertType.ERROR)


async def cmc_log_callback(request: AmherstShipmentRequest, response: ShipmentBookingResponse):
    request = AmherstShipmentRequest.model_validate(request, from_attributes=True)
    await try_update_cmc(shipment=request.shipment, shipment_response=response)

