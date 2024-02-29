from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends
from fastui import AnyComponent, FastUI, components as c
from fastui.events import GoToEvent
from fastui.forms import fastui_form
from pydantic import BaseModel, Field

from amherst.database import get_pfc, get_session
from amherst.front import amui

router = APIRouter()


class Item(BaseModel):
    name: str


@router.post("/items/")
async def create_item(item: Item):
    return {"name": item}


class ToolEnum(str, Enum):
    hammer = "hammer"
    screwdriver = "screwdriver"
    saw = "saw"
    claw_hammer = "claw_hammer"


class SelectForm(BaseModel):
    select_single: ToolEnum = Field(title="Select Single")


class LoginForm(BaseModel):
    password: str


@router.get("/test/")
def test_route(session=Depends(get_session), pfcom=Depends(get_pfc)) -> list[AnyComponent]:
    # return amui.Page.default_page(amui.Text(text="ddddd"))
    return amui.Page.default_page(c.ModelForm(model=SelectForm, submit_url="/api/rout/test_post"))


@router.post("/test_post/", response_model=FastUI, response_model_exclude_none=True)
async def ship_form_post(form: Annotated[SelectForm, fastui_form(SelectForm)]):
    print(form.model_dump())
    return [c.FireEvent(event=GoToEvent(url="/"))]
