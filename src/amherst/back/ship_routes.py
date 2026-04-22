from fastapi import APIRouter, Depends
from loguru import logger
from shipaw.fapi.alerts import Alert, Alerts, AlertType
from shipaw.fapi.routes_html import shipping_form
from starlette.requests import Request
from starlette.responses import HTMLResponse

from amherst.back.backend_pycommence import pycommence_get_one
from amherst.back.backend_search_paginate import SearchRequest
from amherst.back.callbacks import cmc_callback
from amherst.models.amherst_models import AmherstHire, AmherstShipableBase

router = APIRouter()


def get_version():
    from importlib.metadata import PackageNotFoundError, version

    try:
        return version('amherst')
    except PackageNotFoundError:
        return 'unknown'


async def notify_version(request):
    alerts = Alerts.empty()
    sandbox = request.app.shipaw_settings.shipper_live is False
    live_str = 'sandbox' if sandbox else 'live'
    msg = f'AmherstShipper v{get_version()} is {live_str}'
    if sandbox:
        notification_type = AlertType.WARNING
    else:
        notification_type = AlertType.NOTIFICATION
    logger.info(msg)
    alerts += Alert(message=msg, type=notification_type)
    return alerts


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

    # alerts += Alert(message='AAAAAAAAAAAAAAAAAAAAAAAAAAAAA', type=AlertType.NOTIFICATION)
    alerts += await notify_version(request)

    shipment = record.shipment()
    request.app.callback = cmc_callback

    res = await shipping_form(request=request, shipment=shipment)
    return res
