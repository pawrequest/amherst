# from __future__ import annotations

from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import HTMLResponse

from amherst.back.pyc_backend import pycommence_response, row_from_path
from amherst.back.route_depends import SearchRequest, SearchResponse, template_name_from_path
from amherst.config import TEMPLATES
from amherst.models.amherst_models import AMHERST_TABLE_TYPES

router = APIRouter()


@router.get('/multi', response_class=HTMLResponse)
async def multi_shipper(
    request: Request,
):
    return TEMPLATES.TemplateResponse('multi.html', {'request': request})


#
@router.get('/{csrname}/search/{pk_value}')
async def get_srch[T: SearchResponse](
    request: Request,
    search_request: SearchRequest = Depends(SearchRequest.srch_from_path),
    template_name: str = Depends(template_name_from_path),
) -> T:
    resp = await pycommence_response(search_request)
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': resp})


@router.get('/{csrname}/{row_id}')
async def get_row(
    request: Request,
    row: AMHERST_TABLE_TYPES = Depends(row_from_path),
    template_name: str = Depends(template_name_from_path),
) -> HTMLResponse:
    template_name = template_name.replace('.html', '_detail.html')
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'row': row})


@router.get('/{csrname}')
async def get_all(
    request: Request,
    search_request: SearchRequest = Depends(SearchRequest.from_path),
    template_name: str = Depends(template_name_from_path),
) -> SearchResponse:
    response = await pycommence_response(search_request)
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})


# @router.post('/control-box')
# async def control_box_post(request: Request, order: dict):
#     return TEMPLATES.TemplateResponse('controlbox2.html', {'request': request, 'order': order})
#
#
# @router.get('/control-box')
# async def control_box(request: Request):
#     return TEMPLATES.TemplateResponse('controlbox2.html', {'request': request})
#
#

#
# @router.get('/test')
# async def test(request: Request):
#     logger.warning('TEST')
#     return HTMLResponse(content='<h1>Test</h1>')
#
#
# @router.get('/search')
# async def search_get[T: SearchResponse](
#     request: Request,
#     search_request: SearchRequest = Depends(SearchRequest.from_query),
#     template_name: str = Depends(template_name_from_query),
# ) -> HTMLResponse:
#     response: T = await pycommence_response(search_request)
#     return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})
#
#
# @router.post('/search')
# async def search_post[T: SearchResponse](
#     request: Request,
#     search_request: SearchRequest = Depends(SearchRequest.from_body),
#     template_name: str = Depends(template_name_from_query),
# ) -> HTMLResponse:
#     response: T = await pycommence_response(search_request)
#     return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})
#
#
#
# @router.get('/fail/{alert}', response_class=HTMLResponse)
# async def fail(request: Request, alert: str):
#     alert = base64.urlsafe_b64decode(alert).decode('utf-8')
#     logger.exception(f'Error: {alert}')
#     return TEMPLATES.TemplateResponse('fail.html', {'request': request, 'alert': alert})
#
#
# @router.post('/print', response_class=HTMLResponse)
# async def print_label(request: Request, label_path: str = Form(...)):
#     """Endpoint to print the label for a booking."""
#     pawdf.array_pdf.convert_many(Path(label_path), print_files=True)
#     return HTMLResponse(content=f'<p>Printed {label_path}</p>')
#
#
# @router.post('/open-file', response_class=HTMLResponse)
# async def open_label(request: Request, label_path: str = Form(...)):
#     """Endpoint to print the label for a booking."""
#     os.startfile(label_path)
#     return HTMLResponse(content=f'<p>Opened {label_path}</p>')
