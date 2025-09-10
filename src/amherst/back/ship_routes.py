from pathlib import Path

from combadge.core.errors import BackendError
from fastapi import APIRouter, Body, Depends, Form
from loguru import logger
from shipaw.models.pf_shipment import Shipment
from shipaw.pf_config import pf_sett
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressBase, AddressChoice, AddressRecipient
from shipaw.models.pf_msg import Alert, Alerts
from shipaw.ship_types import AlertType, VALID_POSTCODE

from amherst.actions.emailer import send_label_email
from amherst.back.ship_funcs import get_el_client, maybe_get_label, try_book_shipment, try_update_cmc
from amherst.back.ship_queries import record_str_to_record, shipment_f_form, shipment_str_to_shipment
from amherst.back.backend_pycommence import pycommence_get_one
from amherst.config import TEMPLATES
from amherst.models.amherst_models import AMHERST_TABLE_MODELS

router = APIRouter()


@router.get('/ship_form', response_class=HTMLResponse)
async def ship_form(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(pycommence_get_one),
) -> HTMLResponse:
    pf_settings = pf_sett()
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

    if pf_settings.ship_live:
        msg = 'Welcome To Amherst Shipper - Real Shipments will be booked'
    else:
        msg = 'Debug Mode - No Shipments will be booked'
    logger.warning(msg)
    alerts += Alert(message=msg, type=AlertType.NOTIFICATION)

    ctx = {'request': request, 'record': record}

    return TEMPLATES.TemplateResponse(template, ctx)


@router.post('/order_review', response_class=HTMLResponse)
async def order_review(
    request: Request,
    shipment_proposed: Shipment = Depends(shipment_f_form),
    record: AMHERST_TABLE_MODELS = Depends(record_str_to_record),
) -> HTMLResponse:
    alerts = await maybe_alert_phone_number(shipment_proposed)
    logger.info('Shipment Form Posted')
    template = 'ship/order_review.html'
    return TEMPLATES.TemplateResponse(
        template, {'request': request, 'shipment_proposed': shipment_proposed, 'record': record, 'alerts': alerts}
    )


async def maybe_alert_phone_number(shipment_proposed):
    alerts = Alerts.empty()
    if len(
        shipment_proposed.recipient_contact.mobile_phone
    ) != 11 or not shipment_proposed.recipient_contact.mobile_phone[1] in ['1', '2', '7']:
        alerts += Alert(
            type=AlertType.WARNING,
            message='The Mobile phone number must be 11 digits and begin with 01, 02 or 07, no SMS will be sent',
        )
    return alerts


@router.post('/post_confirm', response_class=HTMLResponse)
async def order_confirm(
    request: Request,
    shipment_proposed: Shipment = Depends(shipment_str_to_shipment),
    el_client: ELClient = Depends(get_el_client),
    record: AMHERST_TABLE_MODELS = Depends(record_str_to_record),
) -> HTMLResponse:
    logger.info('Booking Shipment')
    shipment_response, alerts = await try_book_shipment(el_client, shipment_proposed)
    if not shipment_response or not shipment_response.success:
        logger.error(f'Booking failed')
        return TEMPLATES.TemplateResponse(
            'alerts.html',
            {'request': request, 'alerts': alerts, 'shipment_proposed': shipment_proposed, 'record': record},
        )

    # get label
    await maybe_get_label(el_client, shipment_proposed, shipment_response)

    # update commence
    await try_update_cmc(record, shipment_proposed, shipment_response)

    return TEMPLATES.TemplateResponse(
        'ship/order_confirmed.html',
        {
            'request': request,
            'shipment_confirmed': shipment_proposed,
            'response': shipment_response,
            'alerts': alerts,
        },
    )


@router.post('/cand', response_model=list[AddressChoice], response_class=JSONResponse)
async def get_addr_choices(
    request: Request,
    postcode: VALID_POSTCODE = Body(...),
    address: AddressBase = Body(None),
    el_client: ELClient = Depends(get_el_client),
) -> list[AddressChoice]:
    """Fetch candidate address choices for a postcode, optionally scored by closeness to provided address.

    Args:
        postcode: VALID_POSTCODE - postcode to search for
        address: AddressBase - address to compare to candidates
        el_client: ELClient - Parcelforce ExpressLink client
    """
    logger.debug(f'Fetching candidates for {postcode=}, {address=}')
    try:
        res = el_client.get_choices(postcode=postcode, address=address)
        return res
    except BackendError as e:
        alert = Alert(
            message=f'Error fetching candidates: {e}',
            type=AlertType.ERROR,
        )
        request.app.alerts += alert
        logger.warning(f'Error fetching candidates: {e}')
        addr = AddressRecipient(address_line1='BAD API RESPONSE', address_line2=str(e), town='Error', postcode='Error')
        chc = AddressChoice(address=addr, score=0)
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


