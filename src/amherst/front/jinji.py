from datetime import date
from pprint import pprint

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
from shipaw import ELClient, ship_types
from shipaw.models.pf_shared import ServiceCode
from shipaw.ship_types import VALID_POSTCODE

TEMPLATES = Jinja2Templates(directory=str(am_sett().base_dir / 'front' / 'templates'))

router = APIRouter()


@router.post('/post_form/{shiprec_id}', response_class=HTMLResponse)
async def post_form(
    request: Request,
    shiprec_id: int,
    reference: str = Form(''),
    special_instructions: str = Form(''),
    ship_date: date = Form(...),
    boxes: int = Form(...),
    direction: ship_types.ShipDirection = Form(...),
    service: ServiceCode = Form(...),
    # contact: pf_top.Contact = Form(...),
    address: str = Form(...),
    business_name: str = Form(...),
    contact_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    pfcom: ELClient = Depends(am_db.get_el_client),
):
    try:
        return f"<p>Shipment created successfully! <a href='/book/confirm/{shiprec_id}/'>Confirm</a></p>"
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


@router.get('/{shiprec_id}', response_class=HTMLResponse)
async def index(
    request: Request,
    shiprec_id: int,
    session=Depends(am_db.get_session),
    el_client: ELClient = Depends(am_db.get_el_client),
):
    shiprec = await support.get_shiprec(shiprec_id, session)
    addr_choices = el_client.get_choices(shiprec.shipment.address)
    return TEMPLATES.TemplateResponse(
        'base_form.html', {'request': request, 'shiprec': shiprec, 'candidates': addr_choices}
    )
