import os
from pathlib import Path

import pawdf
from fastapi import APIRouter, Depends, Form
from fastapi.encoders import jsonable_encoder
from loguru import logger
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse

from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressChoice
from shipaw.models.pf_msg import ShipmentResponse
from shipaw.ship_types import VALID_POSTCODE
from amherst.back.backend_shipper import (
    book_shipment,
    get_el_client,
    shipment_from_record,
    shipment_request_f_form,
    shipment_str_form_to_shipment,
    wait_label,
)
from amherst.back.backend_pycommence import get_one_f_q2
from amherst.config import TEMPLATES
from amherst.models.amherst_models import AMHERST_TABLE_MODELS, AmherstShipment, AmherstTableBase

router = APIRouter()


async def record_to_form(request, record: AmherstTableBase):
    shipment = await shipment_from_record(record)
    jsonable_ship = jsonable_encoder(shipment)
    jsonable_record = jsonable_encoder(record)
    record_str = record.model_dump_json()
    form_html = TEMPLATES.TemplateResponse(
        'ship/shipping_form_shape2.html',
        {
            'request': request,
            'shipment': jsonable_ship,
            'record_pyd': record,
            'record': jsonable_record,
            'record_str': record_str,
        },
    )
    return form_html


# async def record_to_form2(request, record: AmherstTableBase):
#     shipment = await shipment_from_record2(record)
#     jsonable = jsonable_encoder(shipment)
#     form_html = TEMPLATES.TemplateResponse('ship/shipping_form.html', {'request': request, 'shipment': jsonable})
#     return form_html


@router.get('/form', response_class=HTMLResponse)
async def ship_form(
    request: Request,
    record: AMHERST_TABLE_MODELS = Depends(get_one_f_q2),
        # SearchRequest
):
    logger.warning(f'SHIP FROM ROW ID PATH Row: {record}')
    return await record_to_form(request, record)




@router.get('/candidates', response_model=list[AddressChoice], response_class=JSONResponse)
async def fetch_candidates(
    postcode: VALID_POSTCODE,
    el_client: ELClient = Depends(get_el_client),
):
    res = el_client.get_choices(postcode=postcode)
    return res


@router.post('/post_ship', response_class=HTMLResponse)
async def post_review_form(
    request: Request,
    shipment_request: AmherstShipment = Depends(shipment_request_f_form),
    record_str: str = Form(...),
):
    logger.warning(f'Post Review Form: {shipment_request=}, {record_str=}')
    logger.info(shipment_request.recipient_contact.notifications)
    return TEMPLATES.TemplateResponse(
        'ship/order_review.html',
        {'request': request, 'shipment': shipment_request, 'record_str': record_str},
        # 'ship/order_review.html', {'request': request, 'shipment': shipment_request, 'record': record}
    )


@router.post('/confirm_booking', response_class=HTMLResponse)
async def post_confirm_booking(
    request: Request,
    shipment: AmherstShipment = Depends(shipment_str_form_to_shipment),
    # record: AmherstTableBase = Depends(record_from_json_str_form),
    el_client: ELClient = Depends(get_el_client),
    record_str: str = Form(...),
):
    # todo update commence
    logger.info(f'Confirm booking: {shipment}')
    shipment_response: ShipmentResponse = book_shipment(el_client, shipment)
    if shipment.direction == 'out' or shipment.print_own_label:
        wait_label(shipment_num=shipment_response.shipment_num, dl_path=shipment.label_file, el_client=el_client)
    logger.info(f'Booked Shipment Response: {shipment_response}')
    return TEMPLATES.TemplateResponse(
        'ship/order_confirmed.html', {'request': request, 'shipment': shipment, 'response': shipment_response}
    )


@router.post('/print', response_class=HTMLResponse)
async def print_label(request: Request, label_path: str = Form(...)):
    """Endpoint to print the label for a booking."""
    pawdf.array_pdf.convert_many(Path(label_path), print_files=True)
    return HTMLResponse(content=f'<p>Printed {label_path}</p>')


@router.post('/open-file', response_class=HTMLResponse)
async def open_label(request: Request, label_path: str = Form(...)):
    """Endpoint to print the label for a booking."""
    os.startfile(label_path)
    return HTMLResponse(content=f'<p>Opened {label_path}</p>')


# @router.get('/form', response_class=HTMLResponse)
# async def shipping_form(request: Request):
#     return TEMPLATES.TemplateResponse('ship/shipping_form.html', {'request': request})


# @router.get('/{csrname}')
# async def ship_from_row_id_path(
#         request: Request,
#         row: AMHERST_TABLE_MODELS = Depends(row_from_path_id),
# ):
#     logger.warning(f'SHIP FROM ROW ID PATH Row: {row}')
#     return await record_to_form(request, row)
#     # shipment = await shipment_from_row(row)
#     # return TEMPLATES.TemplateResponse(
#     #     'shipping_form.html', {'request': request, 'shipment': shipment.model_dump_json()}
#     # )

#
# @router.get('/row_id/{csrname}/{row_id}')
# async def ship_from_row_id_path(
#         request: Request,
#         row: AMHERST_TABLE_MODELS = Depends(row_from_path_id),
# ):
#     logger.warning(f'SHIP FROM ROW ID PATH Row: {row}')
#     return await record_to_form(request, row)
#     # shipment = await shipment_from_row(row)
#     # return TEMPLATES.TemplateResponse(
#     #     'shipping_form.html', {'request': request, 'shipment': shipment.model_dump_json()}
#     # )


# @router.get('/pk/{csrname}/{pk_value}', response_class=JSONResponse)
# async def ship_form_pk_value_path(
#         request: Request,
#         resp: SearchResponse = Depends(pycommence_response_q),
# ):
#     if resp.length == 1 or resp.search_request.pk_value == 'Test':
#         row = resp.records[0]
#         return await record_to_form(request, row)
#     else:
#         return resp
#         # show a list


# return response


# def get_label_path(shipment: Shipment, label_dir):
#     logger.debug(f'Getting label path for {shipment.pf_label_filestem}')
#     if shipment.direction != 'out':
#         label_dir = label_dir / shipment.direction
#     lpath = (label_dir / shipment.pf_label_filestem).with_suffix('.pdf')
#     incremented = 2
#     while lpath.exists():
#         logger.warning(f'Label path {lpath} already exists')
#         lpath = lpath.with_name(f'{lpath.stem}_{incremented}{lpath.suffix}')
#         incremented += 1
#     logger.debug(f'Using label path={lpath}')
#     return lpath
