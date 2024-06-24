from datetime import date

from fastapi import APIRouter, Depends, Form
from pydantic import BaseModel, EmailStr, constr, create_model
from sqlmodel import Session
from starlette.responses import HTMLResponse

from amherst.db import get_session
from shipaw import ship_types
from shipaw.models.pf_shared import ServiceCode
from shipaw.ship_types import VALID_POSTCODE

router = APIRouter()


def as_form(cls: type[BaseModel]) -> type[BaseModel]:
    form_params = {
        field_name: (field_info.annotation, Form(... if field_info.is_required() else None))
        for field_name, field_info in cls.model_fields.items()
    }
    new_model = create_model(cls.__name__, **form_params)
    return new_model


def as_form_decon(cls: type[BaseModel]) -> type[BaseModel]:
    form_params = {}
    for field_name, field_info in cls.model_fields:
        form_params[field_name] = (field_info.annotation, Form(... if field_info.required else None))
    new_model = create_model(cls.__name__, **form_params)
    return new_model


@as_form
class PostForm(BaseModel):
    booking_id: int
    direction: ship_types.ShipDirection
    own_label: bool | None = None

    shipping_date: date
    total_number_of_parcels: int
    service_code: ServiceCode

    address_line1: str
    address_line2: str
    address_line3: str
    town: str
    postcode: VALID_POSTCODE

    contact_name: str
    email_address: EmailStr
    business_name: str
    mobile_phone: str

    reference_number1: constr(max_length=24) | None = None
    reference_number2: constr(max_length=24) | None = None
    reference_number3: constr(max_length=24) | None = None
    reference_number4: constr(max_length=24) | None = None
    reference_number5: constr(max_length=24) | None = None
    special_instructions1: constr(max_length=25) | None = None
    special_instructions2: constr(max_length=25) | None = None
    special_instructions3: constr(max_length=25) | None = None
    special_instructions4: constr(max_length=25) | None = None


@router.post('/post_form2/', response_class=HTMLResponse)
async def post_form2(post_form: PostForm, session: Session = Depends(get_session)):
    return HTMLResponse(content=f'<p>Form: {post_form}</p>')
