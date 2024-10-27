# from __future__ import annotations

from fastapi import APIRouter, Depends
from starlette.requests import Request

from amherst.back.backend_pycommence import pycommence_response
from amherst.back.backend_search_paginate import SearchResponse
from amherst.models.maps import detail_template_name, listing_template_name
from amherst.config import TEMPLATES

router = APIRouter()


# @router.get('/multi/', response_class=HTMLResponse)
# async def multi_shipper(
#         request: Request,
# ):
#     return TEMPLATES.TemplateResponse('multi.html', {'request': request})
#

#
# @router.get('/search/{csrname}/{pk_value}')
# async def search_path(
#         request: Request,
#         # search_request: SearchRequest = Depends(SearchRequest.from_path),
#         response: SearchResponse = Depends(search_f_path),
# ) -> SearchResponse:
#     search_request = response.search_request
#     tmplt = CMAP[search_request.csrname].listing_template
#     # template_name: str = await get_tmplt_name('listing', search_request.csrname)
#     # resp = await pycommence_response(search_request)
#     if search_request.max_rtn and response.length > search_request.max_rtn:
#         raise HTTPException(
#             status_code=404,
#             detail=f'Too many items found: Specified {search_request.max_rtn} rows and returned {response.length}'
#         )
#     return TEMPLATES.TemplateResponse(tmplt, {'request': request, 'response': response})
#     # return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})

# @router.get('/pk_search/{csrname}/{pk_value}')
# async def search_path(
#         request: Request,
#         # search_request: SearchRequest = Depends(SearchRequest.from_path),
#         response: SearchResponse = Depends(search_f_path),
# ) -> SearchResponse:
#     search_request = response.search_request
#     tmplt = CMAP[search_request.csrname].listing_template
#     # template_name: str = await get_tmplt_name('listing', search_request.csrname)
#     # resp = await pycommence_response(search_request)
#     if search_request.max_rtn and response.length > search_request.max_rtn:
#         raise HTTPException(
#             status_code=404,
#             detail=f'Too many items found: Specified {search_request.max_rtn} rows and returned {response.length}'
#         )
#     return TEMPLATES.TemplateResponse(tmplt, {'request': request, 'response': response})
#     # return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})


# @router.get('/row_id/{csrname}/{row_id}')
# async def row_id_path(
#         request: Request,
#         row: AMHERST_TABLE_MODELS = Depends(row_from_path_id),
#         # csrname: AmherstTableName = Path(...),
#         template_name=Depends(detail_template_name)
# ) -> HTMLResponse:
#     # template_name: str = await get_tmplt_name('detail', csrname)
#     return TEMPLATES.TemplateResponse(template_name, {'request': request, 'row': row})


@router.get('/{csrname}')
async def listing(
        request: Request,
        search_response: SearchResponse = Depends(pycommence_response),
        template_name: str = Depends(listing_template_name),
) -> SearchResponse:
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': search_response})


@router.get('/detail/{csrname}')
async def detail(
        request: Request,
        search_response: SearchResponse = Depends(pycommence_response),
        template_name: str = Depends(detail_template_name),
) -> SearchResponse:
    row = search_response.records[0]
    return TEMPLATES.TemplateResponse(template_name, {'request': request, 'row': row})

# todo: listing vs detail


#
#
# @router.get('/all/{csrname}')
# async def get_all(
#         request: Request,
#         search_request: SearchRequest = Depends(SearchRequest.get_all),
#         template_name: str = Depends(listing_template_name),
# ) -> SearchResponse:
#     response = await pycommence_response(search_request)
#     return TEMPLATES.TemplateResponse(template_name, {'request': request, 'response': response})
#
#
