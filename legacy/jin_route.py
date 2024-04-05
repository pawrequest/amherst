from fastapi import APIRouter, Depends, Request, responses
from fastapi.responses import HTMLResponse
from sqlmodel import Session
from starlette.templating import Jinja2Templates

from amherst.am_db import get_session
from amherst.models import managers
from amherst.front.support import get_manager
tmpl = r'C:\Users\RYZEN\prdev\workbench\amherst\src\amherst\front\templates'
router = APIRouter()
templates = Jinja2Templates(directory=tmpl)


@router.get("/{man_id}", response_class=HTMLResponse)
async def view(
        request: Request,
        man_id: int,
        session: Session = Depends(get_session),
):
    man_in = await get_manager(man_id, session)
    man_out = managers.BookingManagerOut.model_validate(man_in)
    if not man_out:
        raise ValueError(f'manager id {man_id} not found')

    return templates.TemplateResponse(
        request=request, name="main.html",
        context={'manager': man_out}
    )

@router.get('/', response_class=HTMLResponse)
async def index():
    return responses.RedirectResponse(url='/1')
