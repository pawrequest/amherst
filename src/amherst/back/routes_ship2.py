from fastapi import APIRouter, Body, Depends
from fastapi.encoders import jsonable_encoder
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from amherst.models.maps import maps2
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressBase, AddressChoice
from shipaw.models.pf_msg import ShipmentResponse
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
    AmherstShipment,
    AmherstShipmentResponse,
)
from shipaw.ship_types import VALID_POSTCODE

router = APIRouter()


@router.get('/form2', response_class=HTMLResponse)
async def ship_form_extends_p2(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(get_one),
):
    logger.debug(f'Ship Form shape: {record.row_id=}')
    template = 'ship/form_shape.html'
    return TEMPLATES.TemplateResponse(template, {'request': request, 'record': record})


@router.get('/form_content2', response_class=HTMLResponse)
async def ship_form_content2(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(get_one),
):
    logger.debug(f'Ship Form Content: {record.row_id}')
    template = 'ship/form_content.html'
    return TEMPLATES.TemplateResponse(template, {'request': request, 'record': record})


@router.post('/post_ship2', response_class=HTMLResponse)
async def post_form2(
    request: Request,
    shipment_proposed: AmherstShipment = Depends(shipment_f_form2),
):
    logger.info('Shipment Form Posted')
    template = 'ship/order_review.html'
    return TEMPLATES.TemplateResponse(template, {'request': request, 'shipment_proposed': shipment_proposed})


@router.post('/post_confirm2', response_class=HTMLResponse)
async def post_confirm_booking2(
    request: Request,
    shipment_proposed: AmherstShipment = Depends(amherst_shipment_str_to_shipment),
    el_client: ELClient = Depends(get_el_client),
    pycmc=Depends(pycmc_f_query),
    mapper=Depends(maps2),
    record: AMHERST_TABLE_MODELS = Depends(get_one),
):
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

    if not amherst_ship_response.success:
        alerts = jsonable_encoder(amherst_ship_response.alerts)
        return TEMPLATES.TemplateResponse(
            'alerts.html',
            {'request': request, 'alerts': alerts, 'shipment_proposed': shipment_proposed},
        )
    if shipment_proposed.direction == 'out' or shipment_proposed.print_own_label:
        wait_label(
            shipment_num=amherst_ship_response.shipment_num, dl_path=shipment_proposed.label_file, el_client=el_client
        )

    if mapper.cmc_update_fn:
        update_dict = mapper.cmc_update_fn(shipment_proposed, amherst_ship_response)
        logger.info(f'Updating CMC: {update_dict}')
        pycmc.update_row(update_dict, row_id=shipment_proposed.row_id)
    else:
        logger.info(f'No CMC Update Function for {mapper.category}')

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
