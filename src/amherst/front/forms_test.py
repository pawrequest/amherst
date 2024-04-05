import enum
import typing as _t

from fastapi import APIRouter
from fastui import AnyComponent, FastUI, components as c, events as e
from fastui.events import GoToEvent, PageEvent
from fastui.forms import fastui_form
from pydantic import BaseModel, EmailStr, Field, SecretStr

from pawdantic.pawui import builders

router = APIRouter()
FormKind: _t.TypeAlias = _t.Literal['login', 'select']


@router.get('/{kind}/{manid}', response_model=FastUI, response_model_exclude_none=True)
async def forms_view(kind: FormKind, manid: int) -> list[AnyComponent]:
    return await builders.page_w_alerts(
        components=[
            c.LinkList(
                links=[
                    c.Link(
                        components=[c.Text(text='Login Form')],
                        on_click=PageEvent(
                            name='change-form',
                            push_path=f'/forms_test/login/{manid}',
                            context={'kind': 'login', 'manid': manid}
                        ),
                        active=f'/forms_test/login/{manid}',
                    ),
                    c.Link(
                        components=[c.Text(text='Select Form')],
                        on_click=PageEvent(
                            name='change-form',
                            push_path=f'/forms_test/select/{manid}',
                            context={'kind': 'select', 'manid': manid}
                        ),
                        active=f'/forms_test/select/{manid}',
                    ),
                ],
                mode='tabs',
                class_name='+ mb-4',
            ),
            c.ServerLoad(
                # no f in demo?
                path='/forms_test/content/{kind}/{manid}',
                load_trigger=PageEvent(name='change-form'),
                components=form_content(kind, manid),
            ),
        ],
        title='Forms',
    )


@router.get('/content/{kind}/{manid}', response_model=FastUI, response_model_exclude_none=True)
def form_content(kind: FormKind, manid: int):
    match kind:
        case 'login':
            return [
                c.Heading(text='Login Form', level=2),
                c.Paragraph(text='Simple login form with email and password.'),
                c.ModelForm(model=LoginForm, display_mode='page', submit_url='/api/forms/login'),
            ]
        case 'select':
            return [
                c.Heading(text='Select Form', level=2),
                c.Paragraph(text='Form showing different ways of doing select.'),
                c.ModelForm(model=SelectForm, display_mode='page', submit_url='/api/forms/select'),
            ]
        case _:
            raise ValueError(f'Invalid kind {kind!r}')


class LoginForm(BaseModel):
    email: EmailStr = Field(
        title='Email Address',
        description="Try 'x@y' to trigger server side validation"
    )
    password: SecretStr


@router.post('/login', response_model=FastUI, response_model_exclude_none=True)
async def login_form_post(form: _t.Annotated[LoginForm, fastui_form(LoginForm)]):
    print(form)
    return [c.FireEvent(event=GoToEvent(url='/'))]


class ToolEnum(str, enum.Enum):
    hammer = 'hammer'
    screwdriver = 'screwdriver'
    saw = 'saw'
    claw_hammer = 'claw_hammer'


class SelectForm(BaseModel):
    select_single: ToolEnum = Field(title='Select Single')
    select_multiple: list[ToolEnum] = Field(title='Select Multiple')


@router.post('/select', response_model=FastUI, response_model_exclude_none=True)
async def select_form_post(form: _t.Annotated[SelectForm, fastui_form(SelectForm)]):
    # print(form)
    return [c.FireEvent(event=e.GoToEvent(url='/'))]


class SizeModel(BaseModel):
    width: int = Field(description='This is a field of a nested model')
    height: int = Field(description='This is a field of a nested model')
