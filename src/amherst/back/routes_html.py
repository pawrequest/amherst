import os

from fastapi import APIRouter
from starlette.responses import HTMLResponse

router = APIRouter()


@router.get('/open-file/{filepath}', response_class=HTMLResponse)
async def open_file(filepath: str):
    os.startfile(filepath)
    return HTMLResponse(content='<span>Re</span>')


@router.get('/print-file/{filepath}', response_class=HTMLResponse)
async def print_file(filepath: str):
    os.startfile(filepath, 'print')
    return HTMLResponse(content='<span>Re</span>')


# @router.get('/search')
# async def search(
#     request: Request,
#     pycmc: PyCommence = Depends(pycmc_f_query),
#     search_request: SearchRequest = Depends(SearchRequest.from_query),
#     mapper: AmherstMap = Depends(mapper_from_query_csrname),
# ):
#     search_response: SearchResponse = await pycommence_search(search_request, pycmc)
#     logger.debug(str(search_response))
#     return amherst_settings().templates.TemplateResponse(
#         mapper.templates.listing, {'request': request, 'response': search_response}
#     )
#
