from amherst_core.models import AmherstHire
from amherst_core.models._shipable import AmherstShipableBase as AmherstShipableBaseCore
from fastapi import APIRouter, Depends
from loguru import logger
from pycommence.fapi.search_functions import pycommence_fetch
from pycommence.fapi.search_request_response import SearchRequest
from shipaw.fapi.alerts import Alert, Alerts, AlertType
from shipaw.fapi.routes_html import shipping_form
from shipaw.models.shipment import Shipment
from starlette.requests import Request
from starlette.responses import HTMLResponse

from amherst.back.backend_pycommence import pycommence_get_one

# from amherst.back.backend_search_paginate import SearchRequest
from amherst.back.callbacks import cmc_callback

router = APIRouter()

#
# @router.get('/ship_form_am', response_class=HTMLResponse)
# async def get_shipping_form(
#     request: Request,
#     search_request: SearchRequest = Depends(SearchRequest.from_query),
#     record: AmherstShipableBase = Depends(pycommence_get_one),
# ) -> HTMLResponse:
#     if not record:
#         msg = f'Record not found for {search_request.csrname}: {search_request.pk_value}'
#         logger.error(msg)
#         alert = Alert(message=msg, type=AlertType.ERROR)
#         return HTMLResponse(content=f'<html><body><h1>Error</h1><p>{alert.message}</p></body></html>', status_code=404)
#     alerts: Alerts = request.app.alerts
#     if isinstance(record, AmherstHire) and 'parcelforce' not in record.delivery_method.lower():
#         msg = f'"Parcelforce" not in delivery_method: {record.delivery_method}'
#         logger.warning(msg)
#         alerts += Alert(message=msg, type=AlertType.WARNING)
#
#     shipment = record.shipment()
#     request.app.callback = cmc_callback
#
#     res = await shipping_form(request=request, shipment=shipment)
#     return res
#


@router.get('/ship_form_am2', response_class=HTMLResponse)
async def get_shipping_form2(
    request: Request,
    search_request: SearchRequest = Depends(SearchRequest.from_query),
    record: AmherstShipableBaseCore = Depends(pycommence_fetch),
    # record: AmherstShipableBaseCore = Depends(pycommence_get_one),
) -> HTMLResponse:
    if not record:
        msg = f'Record not found for {search_request.csrname}: {search_request.pk_value}'
        logger.error(msg)
        alert = Alert(message=msg, type=AlertType.ERROR)
        return HTMLResponse(content=f'<html><body><h1>Error</h1><p>{alert.message}</p></body></html>', status_code=404)
    alerts: Alerts = request.app.alerts
    if isinstance(record, AmherstHire) and 'parcelforce' not in record.delivery_method.lower():
        msg = f'"Parcelforce" not in delivery_method: {record.delivery_method}'
        logger.warning(msg)
        alerts += Alert(message=msg, type=AlertType.WARNING)

    shipment_ = record.shipment
    shipment = Shipment.model_validate(shipment_.model_dump())
    request.app.callback = cmc_callback

    res = await shipping_form(request=request, shipment=shipment)
    return res
