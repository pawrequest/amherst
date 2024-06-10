# from __future__ import annotations

from datetime import date

from combadge.core.errors import BackendError
from fastapi import APIRouter, Depends, Form
from loguru import logger
from sqlmodel import Session
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.templating import Jinja2Templates
from urllib3.exceptions import ConnectTimeoutError

from amherst.front.jin_book import process_shipment_request, book_shipment, process_shipment_label
from shipaw import ELClient, Shipment, ship_types
from amherst import am_db
from amherst.am_config import am_sett
from amherst.front import support
from shipaw.models import Contact
from shipaw.models.all_shipment_types import AllShipmentTypes
from shipaw.models.pf_ext import AddressChoice, AddressCollection
from shipaw.models.pf_shared import ServiceCode
from shipaw.ship_types import VALID_POSTCODE

TEMPLATES = Jinja2Templates(directory=str(am_sett().base_dir / 'front' / 'templates'))

router = APIRouter()


@router.post("/confirm_booking", response_class=HTMLResponse)
async def confirm_booking(
        request: Request,
        shiprec_id: int = Form(...),
        shipment_request: str = Form(...),
        el_client: ELClient = Depends(am_db.get_el_client),
        session: Session = Depends(am_db.get_session),
):
    shipment_request = AllShipmentTypes.model_validate_json(shipment_request)

    logger.warning(f'booking_id: {shiprec_id}')
    shiprec = await support.get_shiprec(shiprec_id, session)

    if shiprec.booking_state.booked or shiprec.booking_state.completed:
        logger.error(f'Shipment for {shiprec.record.name} already booked')
        raise ValueError(f'Shipment for {shiprec.record.name} already booked')

    booking_state = book_shipment(el_client, shipment_request)
    label_path = process_shipment_label(el_client, shiprec.sh)
    booking_state.label_downloaded = True
    booking_state.label_dl_path = label_path


    shiprec.booking_state = booking_state

    session.add(shiprec)
    session.commit()
    return HTMLResponse(content=f"<p>Booking Confirmed! {shipment_request}</p>")


@router.post('/post_form/{shiprec_id}', response_class=HTMLResponse)
async def post_form(
        request: Request,
        shiprec_id: int,
        ship_date: date = Form(...),
        boxes: int = Form(...),
        direction: ship_types.ShipDirection = Form(...),
        service: ServiceCode = Form(...),
        contact_name: str = Form(...),
        email: str = Form(...),
        business_name: str = Form(...),
        phone: str = Form(...),
        address_line1: str = Form(...),
        address_line2: str = Form(''),
        address_line3: str = Form(''),
        town: str = Form(...),
        postcode: VALID_POSTCODE = Form(...),
        reference_number1: str = Form(''),
        special_instructions1: str = Form(''),
        reference_number2: str = Form(''),
        special_instructions2: str = Form(''),
        reference_number3: str = Form(''),
        special_instructions3: str = Form(''),
        reference_number4: str = Form(''),
        special_instructions4: str = Form(''),
        pfcom: ELClient = Depends(am_db.get_el_client),
):
    try:
        address = AddressCollection(
            address_line1=address_line1,
            address_line2=address_line2,
            address_line3=address_line3,
            town=town,
            postcode=postcode,
        )
        contact = Contact(
            business_name=business_name,
            contact_name=contact_name,
            email_address=email,
            mobile_phone=phone,
        )
        shipment = Shipment(
            address=address,
            contact=contact,
            service=service,
            ship_date=ship_date,
            boxes=boxes,
            direction=direction,
            reference_number1=reference_number1,
            special_instructions1=special_instructions1,
        )
        shipment = shipment.model_validate(shipment)

        return TEMPLATES.TemplateResponse(
            'review_order.html',
            {'request': request, 'shipment_request': shipment.shipment_request()}
        )
    except (ConnectTimeoutError, BackendError) as e:
        msg = f'Error: {e.__class__.__name__}. Connection Likely Timed Out.\n{str(e)}'
        logger.exception(msg)
        return f'<p>{msg}</p><p>Please refresh the page and try again</p>'
    except Exception as e:
        logger.error(e)
        return f'<p>{str(e)}</p><p>Please refresh the page and try again</p>'


@router.get('/get_candidates', response_class=JSONResponse)
async def get_candidates_json(  #
        postcode: VALID_POSTCODE,
        el_client: ELClient = Depends(am_db.get_el_client),
):
    res = el_client.candidates_json(postcode)
    return res


@router.get('/get_candidatesp', response_model=list[AddressChoice], response_class=JSONResponse)
async def get_candidatesp(
        postcode: VALID_POSTCODE,
        el_client: ELClient = Depends(am_db.get_el_client),
):
    res = el_client.get_choices(postcode)
    return res


@router.get('/{shiprec_id}', response_class=HTMLResponse)
async def index(
        request: Request,
        shiprec_id: int,
        session=Depends(am_db.get_session),
        el_client: ELClient = Depends(am_db.get_el_client),
):
    shiprec = await support.get_shiprec(shiprec_id, session)
    shiprec.model_dump_json(by_alias=True)
    addr_choices = el_client.get_choices(
        shiprec.shipment.address.postcode,
        shiprec.shipment.address
    )
    return TEMPLATES.TemplateResponse(
        'base_form.html', {'request': request, 'shiprec': shiprec, 'candidates': addr_choices}
    )
