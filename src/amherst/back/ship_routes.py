from fastapi import APIRouter, Depends
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse

from amherst.back.backend_pycommence import pycommence_get_one
from amherst.back.callbacks import cmc_log_callback
from amherst.models.amherst_models import AmherstHire, AmherstShipableBase
from shipaw.fapi.routes_html import shipping_form
from shipaw.fapi.alerts import Alert, AlertType, Alerts

router = APIRouter()


@router.get('/ship_form_am', response_class=HTMLResponse)
async def get_shipping_form(
    request: Request,
    record: AmherstShipableBase = Depends(pycommence_get_one),
) -> HTMLResponse:
    alerts: Alerts = request.app.alerts
    if isinstance(record, AmherstHire) and 'parcelforce' not in record.delivery_method.lower():
        msg = f'"Parcelforce" not in delivery_method: {record.delivery_method}'
        logger.warning(msg)
        alerts += Alert(message=msg, type=AlertType.WARNING)

    shipment = record.shipment()
    request.app.callback = cmc_log_callback

    return await shipping_form(request=request, shipment=shipment)

