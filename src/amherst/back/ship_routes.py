from pathlib import Path

from combadge.core.errors import BackendError
from fastapi import APIRouter, Body, Depends, Form
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, PlainTextResponse

from amherst.actions.emailer import send_label_email
from amherst.back.backend_pycommence import pycommence_get_one
from amherst.back.ship_funcs import get_el_client, try_book_shipment, try_update_cmc
from amherst.back.ship_queries import (
    record_str_to_record,
    shipment_f_form,
    shipment_req_str_to_shipment2,
    shipment_str_to_shipment,
)
from amherst.config import amherst_settings
from amherst.models.amherst_models import AMHERST_TABLE_MODELS
from shipaw.agnostic.address import Address, AddressChoice, Contact
from shipaw.agnostic.base import ShipawBaseModel
from shipaw.config import shipaw_settings
from shipaw.agnostic.requests import ProviderName, ShipmentRequestAgnost
from shipaw.agnostic.responses import Alert, AlertType, Alerts
from shipaw.agnostic.shipment import Shipment
from shipaw.parcelforce.address import AddressBase
from shipaw.parcelforce.client import ParcelforceClient

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

    if shipaw_settings().shipper_live:
        msg = 'Shipper Live is True - Real Shipments will be booked'
    else:
        msg = 'Shipper_live is False - No Shipments will be booked'
    logger.warning(msg)
    alerts += Alert(message=msg, type=AlertType.NOTIFICATION)

    ctx = {'request': request, 'record': record}
    return amherst_settings().templates.TemplateResponse(template, ctx)


@router.post('/order_review', response_class=HTMLResponse)
async def order_review2(
    request: Request,
    shipment: Shipment = Depends(shipment_f_form),
    record: AMHERST_TABLE_MODELS = Depends(record_str_to_record),
    provider_name: ProviderName = Form(...),
) -> HTMLResponse:
    alerts = await maybe_alert_phone_number(shipment.remote_full_contact.contact)
    logger.info('Shipment Form Posted')
    template = 'ship/order_review.html'
    ship_req = ShipmentRequestAgnost(shipment=shipment, provider_name=provider_name)
    return amherst_settings().templates.TemplateResponse(
        template, {'request': request, 'shipment_request': ship_req, 'record': record, 'alerts': alerts}
    )


#
# @router.post('/order_review1', response_class=HTMLResponse)
# async def order_review(
#     request: Request,
#     shipment: Shipment = Depends(shipment_f_form),
#     record: AMHERST_TABLE_MODELS = Depends(record_str_to_record),
#     provider_name: ProviderName = Form(...),
# ) -> HTMLResponse:
#     alerts = await maybe_alert_phone_number(shipment)
#     logger.info('Shipment Form Posted')
#     template = 'ship/order_review.html'
#     ship_req = ShipmentRequestAgnost(shipment=shipment, provider_name=provider_name)
#     return amherst_settings().templates.TemplateResponse(
#         template, {'request': request, 'shipment_request': ship_req, 'record': record, 'alerts': alerts}
#     )


async def maybe_alert_phone_number(contact: Contact):
    """Alert if phone number is not 11 digits or does not start with 01, 02 or 07. (parcelforce requirement)"""
    alerts = Alerts.empty()
    if len(contact.mobile_phone) != 11 or not contact.mobile_phone[1] in [
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
async def order_confirm2(
    request: Request,
    shipment_req: ShipmentRequestAgnost = Depends(shipment_req_str_to_shipment2),
    record: AMHERST_TABLE_MODELS = Depends(record_str_to_record),
) -> HTMLResponse:
    logger.info('Booking Shipment')
    shipment_response = await try_book_shipment(shipment_req)
    shipment_req.provider.handle_response(shipment_req, shipment_response)

    if not shipment_response or not shipment_response.success:
        logger.error(f'Booking failed')
        return amherst_settings().templates.TemplateResponse(
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

    return amherst_settings().templates.TemplateResponse(
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


# @router.get('/home_mobile_phone', response_class=PlainTextResponse)
# async def home_mobile_phone():
#     return shipaw_settings().mobile_phone


@router.get('/home_mobile_phone', response_class=HTMLResponse)
async def home_mobile_phone():
    mobile_phone = shipaw_settings().mobile_phone
    return f"""
    <input type="tel" id="mobile_phone" name="mobile_phone" value="{mobile_phone}" required>
    """


@router.post('/cand', response_model=list[AddressChoice], response_class=JSONResponse)
async def get_addr_choices(
    request: Request,
    body: AddressRequest = Body(...),
    el_client: ParcelforceClient = Depends(get_el_client),
) -> list[AddressChoice]:
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
    # address = ParcelforceProvider.provider_address_only(address, mode='pydantic') if address else None
    address = AddressBase.from_generic(address)

    try:
        res = el_client.get_choices(postcode=postcode, address=address)
        res_agnost = [
            AddressChoice(address=AddressBase.to_generic(_.address, business_name=''), score=_.score) for _ in res
        ]
        return res_agnost
    except BackendError as e:
        alert = Alert(
            message=f'Error fetching candidates: {e}',
            type=AlertType.ERROR,
        )
        request.app.alerts += alert  # todo is this received frontend?
        logger.warning(f'Error fetching candidates: {e}')
        addr = Address(address_lines=['ERROR:', str(e)], town='Error', postcode='Error', business_name='Error')
        chc = AddressChoice(address=addr, score=0)
        return [chc]


@router.post('/email_label', response_class=HTMLResponse)
async def email_label(
    shipment: Shipment = Depends(shipment_str_to_shipment),
    label: Path = Form(...),
):
    shipment._label_file = label
    await send_label_email(shipment)
    return '<span>Re</span>'
