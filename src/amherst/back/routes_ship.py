from fastapi import APIRouter, Body, Depends, Query
from fastapi.encoders import jsonable_encoder
from loguru import logger
from pycommence.pycommence_v2 import PyCommence
from shipaw.pf_config import pf_sett
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from amherst.actions.emailer import send_label_email
from amherst.models.maps import AmherstMap, get_mapper
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressBase, AddressChoice
from shipaw.models.pf_msg import Alert, Alerts, ShipmentResponse
from amherst.back.backend_shipper import (
    amherst_shipment_str_to_shipment,
    book_shipment,
    get_el_client,
    shipment_f_form2,
    wait_label,
)
from amherst.back.backend_pycommence import get_one, pycmc_f_query
from amherst.config import TEMPLATES
from amherst.models.amherst_models import (
    AMHERST_TABLE_MODELS,
    AmherstShipmentOut,
    AmherstShipmentResponse,
)
from shipaw.ship_types import AlertType, VALID_POSTCODE

router = APIRouter()


@router.get('/form2', response_class=HTMLResponse)
async def ship_form_extends_p2(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(get_one),
):
    pf_settings = pf_sett()
    ship_live = pf_settings.ship_live
    logger.debug(f'Ship Form shape: {record.row_id=}')
    template = 'ship/form_shape.html'
    ctx = {'request': request, 'record': record, 'ship_live': ship_live}
    if 'parcelforce' not in record.delivery_method.lower():
        msg = '"Parcelforce" not in delivery_method'
        logger.warning(msg)
        alert = Alert(code=1, message=msg, type=AlertType.WARNING)
        alerts = Alerts(alert=[alert])
        ctx.update({'alerts': alerts})
    return TEMPLATES.TemplateResponse(template, ctx)


@router.get('/form_content2', response_class=HTMLResponse)
async def ship_form_content2(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(get_one),
):
    logger.debug(f'Ship Form Content: {record.row_id}')
    pf_settings = pf_sett()
    logger.warning(pf_settings.model_dump())
    logger.warning(pf_settings.model_dump())
    logger.warning(pf_settings.model_dump())
    logger.warning(pf_settings.model_dump())
    ship_live = pf_settings.ship_live
    template = 'ship/form_content.html'
    ctx = {'request': request, 'record': record, 'ship_live': ship_live}
    # if 'parcelforce' not in record.delivery_method.lower():
    #     alert = Alert(code=1, message='"Parcelforce" not in delivery_method', type=AlertType.WARNING)
    #     alerts = Alerts(alert=[alert])
    #     ctx.update({'alerts': alerts})
    return TEMPLATES.TemplateResponse(template, ctx)


@router.post('/post_ship2', response_class=HTMLResponse)
async def post_form2(
    request: Request,
    shipment_proposed: AmherstShipmentOut = Depends(shipment_f_form2),
):
    logger.info('Shipment Form Posted')
    template = 'ship/order_review.html'
    return TEMPLATES.TemplateResponse(template, {'request': request, 'shipment_proposed': shipment_proposed})


@router.post('/post_confirm2', response_class=HTMLResponse)
async def post_confirm_booking2(
    request: Request,
    shipment_proposed: AmherstShipmentOut = Depends(amherst_shipment_str_to_shipment),
    el_client: ELClient = Depends(get_el_client),
    pycmc: PyCommence = Depends(pycmc_f_query),
    mapper: AmherstMap = Depends(get_mapper),
    # record: AMHERST_TABLE_MODELS = Depends(get_one),
):
    record_dict = pycmc.read_row(row_id=shipment_proposed.row_id)
    record = mapper.record_model.model_validate(record_dict)
    logger.info('Booking Shipent')
    shipment_response: ShipmentResponse = book_shipment(el_client, shipment_proposed.shipment())
    amherst_ship_response: AmherstShipmentResponse = AmherstShipmentResponse(
        row_id=shipment_proposed.row_id, category=shipment_proposed.category, **shipment_response.model_dump()
    )
    # amherst_ship_response: AmherstShipmentResponse = AmherstShipmentResponse.model_validate(
    #     shipment_response.model_copy(update={'row_id': shipment_proposed.row_id, 'category': shipment_proposed.category}),
    #     from_attributes=True,
    # )
    logger.info(f'Booked AmherstShipment Response: {amherst_ship_response}')

    # handle alerts
    if not amherst_ship_response.success:
        alerts = jsonable_encoder(amherst_ship_response.alerts)
        return TEMPLATES.TemplateResponse(
            'alerts.html',
            {'request': request, 'alerts': alerts, 'shipment_proposed': shipment_proposed},
        )

    # get label
    if shipment_proposed.direction == 'out' or shipment_proposed.print_own_label:
        wait_label(
            shipment_num=amherst_ship_response.shipment_num, dl_path=shipment_proposed.label_file, el_client=el_client
        )

    # update commence
    if mapper.cmc_update_fn2:
        update_dict = await mapper.cmc_update_fn2(record, shipment_proposed, amherst_ship_response)
        logger.info(f'Updating CMC V2: {update_dict}')
        pycmc.update_row(update_dict, row_id=shipment_proposed.row_id)

    else:
        logger.warning('NO CMC UPDATE FUNCTION')

    return TEMPLATES.TemplateResponse(
        'ship/order_confirmed.html',
        {'request': request, 'shipment_confirmed': shipment_proposed, 'response': amherst_ship_response},
    )


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


@router.get('/email_label', response_class=HTMLResponse)
async def email_label(
    request: Request,
    filepath: str = Query(...),
    addresses: list[str] = Query(...),
):
    logger.info(f'Emailing {filepath=} to {addresses=}')
    await send_label_email(addresses=addresses, label=filepath)
    return "Email Created"
