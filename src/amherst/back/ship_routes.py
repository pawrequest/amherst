from pathlib import Path

from combadge.core.errors import BackendError
from fastapi import APIRouter, Body, Depends, Form
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from amherst.actions.emailer import send_label_email
from amherst.back.backend_pycommence import pycommence_get_one
from amherst.back.ship_funcs import get_el_client, try_book_shipment, try_update_cmc
from amherst.back.ship_queries import (
    record_str_to_record,
    shipment_f_form,
    shipment_req_str_to_shipment,
    shipment_str_to_shipment,
)
from amherst.config import TEMPLATES
from amherst.models.amherst_models import AMHERST_TABLE_MODELS
from shipaw.agnostic.address import Address, AddressChoiceAgnost
from shipaw.agnostic.base import ShipawBaseModel
from shipaw.agnostic.requests import ProviderName, ShipmentRequestAgnost
from shipaw.agnostic.responses import Alert, AlertType, Alerts
from shipaw.agnostic.shipment import Shipment
from shipaw.parcelforce.client import ParcelforceClient
from shipaw.parcelforce.config import pf_settings
from shipaw.parcelforce.provider import ParcelforceProvider

router = APIRouter()


@router.get('/ship_form', response_class=HTMLResponse)
async def ship_form(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(pycommence_get_one),
) -> HTMLResponse:
    # pf_settings = pf_sett()
    template = 'ship/form_shape.html'
    alerts: Alerts = request.app.alerts

    if any(['prdev' in str(_).lower() for _ in Path(__file__).parents]):
        msg = '"prdev" in cwd tree - BETA MODE - This is a development version of Amherst Shipper'
        logger.warning(msg)
        alerts += Alert(message=msg, type=AlertType.WARNING)

    if hasattr(record, 'delivery_method') and 'parcelforce' not in record.delivery_method.lower():
        msg = f'"Parcelforce" not in delivery_method: {record.delivery_method}'
        logger.warning(msg)
        alerts += Alert(message=msg, type=AlertType.WARNING)

    # if pf_settings.ship_live:
    #     msg = 'Welcome To Amherst Shipper - Real Shipments will be booked'
    else:
        msg = 'Debug Mode - No Shipments will be booked'
    logger.warning(msg)
    alerts += Alert(message=msg, type=AlertType.NOTIFICATION)

    ctx = {'request': request, 'record': record}

    return TEMPLATES.TemplateResponse(template, ctx)


@router.post('/order_review', response_class=HTMLResponse)
async def order_review(
    request: Request,
    shipment: Shipment = Depends(shipment_f_form),
    record: AMHERST_TABLE_MODELS = Depends(record_str_to_record),
    provider_name: ProviderName = Form(...),
) -> HTMLResponse:
    alerts = await maybe_alert_phone_number(shipment)
    logger.info('Shipment Form Posted')
    template = 'ship/order_review.html'
    ship_req = ShipmentRequestAgnost(shipment=shipment, provider_name=provider_name)
    return TEMPLATES.TemplateResponse(
        template, {'request': request, 'shipment_request': ship_req, 'record': record, 'alerts': alerts}
    )


async def maybe_alert_phone_number(shipment: Shipment):
    """Alert if phone number is not 11 digits or does not start with 01, 02 or 07. (parcelforce requirement)"""
    alerts = Alerts.empty()
    if len(shipment.recipient.contact.mobile_phone) != 11 or not shipment.recipient.contact.mobile_phone[1] in [
        '1',
        '2',
        '7',
    ]:
        alerts += Alert(
            type=AlertType.WARNING,
            message='The Mobile phone number must be 11 digits and begin with 01, 02 or 07, no SMS will be sent',
        )
    return alerts


@router.post('/post_confirm', response_class=HTMLResponse)
async def order_confirm(
    request: Request,
    shipment_req: ShipmentRequestAgnost = Depends(shipment_req_str_to_shipment),
    record: AMHERST_TABLE_MODELS = Depends(record_str_to_record),
) -> HTMLResponse:
    logger.info('Booking Shipment')
    shipment_response = await try_book_shipment(shipment_req)
    if not shipment_response or not shipment_response.success:
        logger.error(f'Booking failed')
        return TEMPLATES.TemplateResponse(
            'alerts.html',
            {
                'request': request,
                'alerts': shipment_response.alerts,
                'shipment': shipment_req.shipment,
                'record': record,
            },
        )

    # get label
    await shipment_response.write_label_file()

    # update commence
    await try_update_cmc(record, shipment_req.shipment, shipment_response)

    return TEMPLATES.TemplateResponse(
        'ship/order_confirmed.html',
        {
            'request': request,
            'shipment': shipment_req.shipment,
            'response': shipment_response,
            'alerts': shipment_response.alerts,
        },
    )


class AddressRequest(ShipawBaseModel):
    postcode: str
    address: Address | None = None


@router.post('/cand', response_model=list[AddressChoiceAgnost], response_class=JSONResponse)
async def get_addr_choices(
    request: Request,
    body: AddressRequest = Body(...),
    el_client: ParcelforceClient = Depends(get_el_client),
) -> list[AddressChoiceAgnost]:
    """Fetch candidate address choices for a postcode, optionally scored by closeness to provided address.

    Args:
        request: Request - FastAPI request object
        body: AddressRequest - request body containing postcode and optional address
        el_client: ELClient - Parcelforce ExpressLink client
    """
    # address = ParcelforceProvider.provider_address(address)
    postcode = body.postcode
    address = body.address
    logger.debug(f'Fetching candidates for {postcode=}, {address=}')
    address = ParcelforceProvider.provider_address_only(address, mode='pydantic') if address else None

    try:
        res = el_client.get_choices(postcode=postcode, address=address)
        res_agnost = [
            AddressChoiceAgnost(address=ParcelforceProvider.generic_address_only(_.address), score=_.score) for _ in res
        ]
        return res_agnost
    except BackendError as e:
        alert = Alert(
            message=f'Error fetching candidates: {e}',
            type=AlertType.ERROR,
        )
        request.app.alerts += alert  # todo is this received frontend?
        logger.warning(f'Error fetching candidates: {e}')
        addr = Address(address_lines=['ERROR:', str(e)], town='Error', postcode='Error')
        chc = AddressChoiceAgnost(address=addr, score=0)
        return [chc]


@router.post('/email_label', response_class=HTMLResponse)
async def email_label(
    request: Request,
    shipment: Shipment = Depends(shipment_str_to_shipment),
    label: Path = Form(...),
):
    shipment._label_file = label
    await send_label_email(shipment)
    return '<span>Re</span>'


res = "Shipping Label TO Test Default Del Building _ ON 2025-09-24.pdf"