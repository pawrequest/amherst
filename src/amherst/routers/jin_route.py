from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from sqlmodel import Session
from starlette.templating import Jinja2Templates

from amherst.am_db import get_session
from amherst.models import managers
from amherst.routers.back_funcs import get_manager

router = APIRouter()

templates = Jinja2Templates(directory="templates")


@router.get("/{man_id}", response_class=HTMLResponse)
async def index(
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

