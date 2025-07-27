from pathlib import Path

from fastapi import APIRouter, Body, Depends, Form
from loguru import logger
from pawdf.array_pdf.array_p import on_a4
from pycommence.pycommence import pycommence_context
from shipaw.models.pf_shipment import Shipment
from shipaw.pf_config import pf_sett
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressBase, AddressChoice
from shipaw.models.pf_msg import Alert, ShipmentResponse, Alerts
from shipaw.ship_types import AlertType, ShipDirection, VALID_POSTCODE, ExpressLinkError

from amherst.actions.emailer import send_label_email
from amherst.models.maps import AmherstMap, mapper_from_query_csrname
from amherst.back.backend_shipper import (
    amherst_shipment_str_to_shipment,
    book_shipment,
    get_el_client,
    record_str_to_record,
    shipment_f_form,
    shipment_str_to_shipment,
    wait_label,
)
from amherst.back.backend_pycommence import get_one
from amherst.config import TEMPLATES
from amherst.models.amherst_models import (
    AMHERST_SHIPMENT_TYPES,
    AMHERST_TABLE_MODELS,
)

router = APIRouter()


@router.get('/ship_form', response_class=HTMLResponse)
async def ship_form(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(get_one),
):
    pf_settings = pf_sett()
    logger.debug(f'Ship Form shape: {record.row_id=}')
    template = 'ship/form_shape.html'
    alerts: Alerts = request.app.alerts

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
):
    logger.info('Shipment Form Posted')
    template = 'ship/order_review.html'
    return TEMPLATES.TemplateResponse(
        template, {'request': request, 'shipment_proposed': shipment_proposed, 'record': record}
    )


@router.post('/post_confirm', response_class=HTMLResponse)
async def order_confirm(
    request: Request,
    shipment_proposed: Shipment = Depends(shipment_str_to_shipment),
    el_client: ELClient = Depends(get_el_client),
    record: AMHERST_TABLE_MODELS = Depends(record_str_to_record),
):
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


async def maybe_get_label(el_client, shipment_proposed, shipment_response):
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
        mapper: AmherstMap = await mapper_from_query_csrname(record.category)
        if mapper.cmc_update_fn:
            update_dict = await mapper.cmc_update_fn(record, shipment_proposed, shipment_response)
            logger.info(f'Updating CMC: {update_dict}')
            with pycommence_context(csrname=record.category) as pycmc1:
                pycmc1.update_row(update_dict, row_id=record.row_id)

        else:
            logger.warning('NO CMC UPDATE FUNCTION')

    except ValueError as e:
        msg = f'Error updating Commence: {e}'
        logger.exception(e)
        shipment_response.alerts += Alert(message=msg, type=AlertType.ERROR)


@router.post('/cand', response_model=list[AddressChoice], response_class=JSONResponse)
async def get_addr_choices(
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
    res = el_client.get_choices(postcode=postcode, address=address)
    return res


@router.post('/email_label', response_class=HTMLResponse)
async def email_label(
    request: Request,
    shipment: AMHERST_SHIPMENT_TYPES = Depends(amherst_shipment_str_to_shipment),
    label: Path = Form(...),
):
    shipment._label_file = label
    logger.warning(shipment)
    await send_label_email(shipment)
    return '<span>Re</span>'


# @router.post('/email_label2', response_class=HTMLResponse)
# async def email_label2(
#     request: Request,
#     shipment: AMHERST_SHIPMENT_TYPES = Depends(amherst_shipment_str_to_shipment),
#     label: Path = Form(...),
# ):
#     label_ona4 = label.with_stem(label.stem + '_on_a4')
#     # label_ona4 = label.with_suffix('.on_a4.pdf')
#     pawdf.array_pdf.array_p.on_a4(label, output_file=label_ona4)
#     shipment._label_file = label_ona4
#     logger.warning(shipment)
#     await send_label_email(shipment)
#     return 'Email Created'


#
# @router.get('/email_label1', response_class=HTMLResponse)
# async def email_label1(
#     request: Request,
#     filepath: Path = Query(...),
#     addresses: list[str] = Query(...),
# ):
#     logger.info(f'Emailing {filepath=} to {addresses=}')
#     await send_label_email(addresses=addresses, label=filepath)
#     return "Email Created"


# @router.post('/post_confirm', response_class=HTMLResponse)
# async def order_confirm1(
#     request: Request,
#     shipment_proposed: Shipment = Depends(shipment_str_to_shipment),
#     el_client: ELClient = Depends(get_el_client),
#     record: AMHERST_TABLE_MODELS = Depends(record_str_to_record),
# ):
#     logger.info('Booking Shipment')
#     shipment_response: ShipmentResponse = book_shipment(el_client, shipment_proposed)
#     logger.info(f'Booked Shipment Response: {shipment_response}')
#
#     # handle alerts
#     alerts = shipment_response.alerts
#     if not shipment_response.success:
#         # alerts = jsonable_encoder(amherst_ship_response.alerts)
#         return TEMPLATES.TemplateResponse(
#             'alerts.html',
#             {'request': request, 'alerts': alerts, 'shipment_proposed': shipment_proposed, 'record': record},
#         )
#
#     # get label
#     await maybe_get_label(el_client, shipment_proposed, shipment_response)
#
#     # update commence
#     await try_update_cmc(record, shipment_proposed, shipment_response)
#
#     return TEMPLATES.TemplateResponse(
#         'ship/order_confirmed.html',
#         {
#             'request': request,
#             'shipment_confirmed': shipment_proposed,
#             'response': shipment_response,
#             'alerts': alerts,
#         },
#     )

