from __future__ import annotations, annotations

from datetime import date
from typing import Optional

from fastui.events import PageEvent
from pydantic import BaseModel, Field, field_validator, model_validator
from fastui import components as c
from thefuzz import process

from amherst.models import HireDB
from amherst.shipping.pfcom import AmShipper
from pawsupport.convert import get_ordinal_suffix
from shipr import enums as ele, types as elt
from pawsupport.fastui_ps import fui
from shipr.express.types import AddressPF
from . import amui, css
from ..models.shared import AmherstFields


# from amherst.models import HireWSubModels

class HireState(BaseModel):
    boxes: int = 1
    ship_date: Optional[date] = Field(default_factory=date.today)
    ship_service: Optional[ele.ServiceCode] = ele.ServiceCode.EXPRESS24
    candidates: list[elt.AddressPF] = Field(default_factory=list)
    address: Optional[elt.AddressPF] = Field(default=None)
    contact: Optional[elt.ContactPF] = Field(default=None)
    address_choice: Optional[elt.AddressChoice] = Field(default=None)
    ...

    @field_validator('ship_date', mode='after')
    def validate_ship_date(cls, v):
        tod = date.today()
        return v if v >= tod else tod


class HireUI(BaseModel):
    ...
    pfcom: AmShipper = Field(default_factory=AmShipper.from_env)
    hire: HireDB
    state: Optional[HireState] = None

    # @field_validator('state', mode='after')
    # def state_is_none(cls, v, info):
    #     v = v or HireState(
    #         boxes=info.data.get('hire').boxes,
    #     )
    #     return v


    @model_validator(mode='after')
    def set_state(self):
        if self.state is None:
            self.state = HireState()
        self.state.boxes = self.state.boxes or self.hire.boxes
        self.state.ship_date = self.state.ship_date or self.hire.ship_date
        self.state.contact = self.state.contact or self.hire.contact
        self.state.candidates = (self.state.candidates
                                 or self.pfcom.get_candidates(self.hire.address.postcode))
        self.state.address_choice = (self.state.address_choice
                                     or self.pfcom.choose_hire_address(self.hire.address))
        self.state.address = self.state.address or self.state.address_choice.address
        return self


    async def get_components(self) -> list[c.AnyComponent]:
        return fui.Container.wrap(
            await self.address_section(),
            await self.details_section()
        )

    async def get_page(self) -> list[c.AnyComponent]:
        return amui.Page.default_page(
            await self.get_components(),
            title="Hire Shipping"
        )

    async def address_section(self):
        async def amherst_address_col():
            return amui.Col.wrap(
                fui.Text(text=self.hire.record.get(AmherstFields.CUSTOMER)),
                *await address_col(self.hire.address),
                wrap_inner=amui.Row
            )

        async def address_buttons_div(outer_wrap=amui.Col, wrap_inner=amui.Row):
            ret = outer_wrap.wrap(
                fui.Text(text=f'Address score: {self.state.address_choice.score}'),
                c.Button(text="Choose this address"),
                c.Button(text="Enter address manually", on_click=None),
                c.Button(
                    text='Choose a Different Address',
                    on_click=PageEvent(name='address-chooser')
                ),
                amui.address_chooser_modal(self.state.candidates),
                wrap_inner=wrap_inner,
            )
            return ret

        return amui.Row(
            components=[
                await amherst_address_col(),
                await address_buttons_div(),
                await address_col(self.state.address, wrap_in=amui.Col)
            ]
        )

    async def details_section(self):
        async def boxes_btn():
            num_b = self.state.boxes
            return c.Button(text=f'{num_b} Boxes', on_click=None, class_name=css.BOXES_BTN)

        async def date_btn():
            date_ = self.state.ship_date
            fstr = f'%A %d{get_ordinal_suffix(date_.day)} %B'
            text = f'{date_:{fstr}}'
            return c.Button(
                text=text,
                on_click=None,
            )

        return amui.Row(
            components=[
                await date_btn(),
                await boxes_btn()
            ]
        )


async def address_col(address: AddressPF, wrap_in=None):
    txts = fui.Text.all_text(address)
    if wrap_in:
        return wrap_in.wrap(*txts, wrap_inner=amui.Row)
    return txts
