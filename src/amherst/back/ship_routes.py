from fastapi import APIRouter, Depends
from loguru import logger
from shipaw.fapi.alerts import Alert, Alerts, AlertType
from shipaw.fapi.routes_html import shipping_form
from starlette.requests import Request
from starlette.responses import HTMLResponse

from amherst.back.backend_pycommence import pycommence_get_one
from amherst.back.backend_search_paginate import SearchRequest
from amherst.back.callbacks import cmc_log_callback
from amherst.models.amherst_models import AmherstHire, AmherstShipableBase

router = APIRouter()


@router.get('/ship_form_am', response_class=HTMLResponse)
async def get_shipping_form(
        request: Request,
        search_request: SearchRequest = Depends(SearchRequest.from_query),
        record: AmherstShipableBase = Depends(pycommence_get_one),
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

    shipment = record.shipment()
    request.app.callback = cmc_log_callback

    res = await shipping_form(request=request, shipment=shipment)
    return res
