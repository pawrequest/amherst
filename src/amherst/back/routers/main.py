from __future__ import annotations as _annotations

from fastapi import APIRouter, Depends
from fastui import FastUI
from sqlmodel import Session

from DecodeTheBot.core.database import get_session
from DecodeTheBot.routers.eps import episode_list_view

router = APIRouter()


@router.get("/", response_model=FastUI, response_model_exclude_none=True)
def api_index(page: int = 1, guru_name: str | None = None, session: Session = Depends(get_session)):
    return episode_list_view(page, guru_name, session)


@router.get("/{path:path}", status_code=404)
async def api_404():
    # so we don't fall through to the index page
    return {"message": "Not Found"}
