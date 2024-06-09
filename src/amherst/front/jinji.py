from datetime import date

from combadge.core.errors import BackendError
from fastapi import APIRouter, Depends, Form
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse
from starlette.templating import Jinja2Templates
from urllib3.exceptions import ConnectTimeoutError

from amherst import am_db
from amherst.am_config import am_sett
from amherst.front import support
from shipaw import ELClient, Shipment, ship_types
from shipaw.models import Contact
from shipaw.models.pf_ext import AddressCollection, AddressChoice
from shipaw.models.pf_shared import ServiceCode
from shipaw.ship_types import VALID_POSTCODE

TEMPLATES = Jinja2Templates(directory=str(am_sett().base_dir / 'front' / 'templates'))

router = APIRouter()


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
    reference1: str = Form(''),
    special_instructions1: str = Form(''),
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
            reference1=reference1,
            special_instructions1=special_instructions1,
        )
        shipment = shipment.model_validate(shipment)

        return f'<p>Shipment created successfully! {shipment}</p>'
        # return f"<p>Shipment created successfully! <a href='/book/confirm/{shiprec_id}/{shipment.model_dump_64()}'>Confirm</a></p>"
    except (ConnectTimeoutError, BackendError) as e:
        msg = f'Error: {e.__class__.__name__}. Connection Likely Timed Out.\n{str(e)}'
        logger.exception(msg)
        return f'<p>{msg}</p><p>Please refresh the page and try again</p>'
    except Exception as e:
        logger.error(e)
        return f'<p>{str(e)}</p><p>Please refresh the page and try again</p>'


@router.get('/get_candidates', response_class=JSONResponse)
async def get_candidates(
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
    addr_choices = el_client.get_choices(shiprec.shipment.address.postcode, shiprec.shipment.address)
    return TEMPLATES.TemplateResponse(
        'base_form.html', {'request': request, 'shiprec': shiprec, 'candidates': addr_choices}
    )
