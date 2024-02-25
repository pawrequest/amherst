from __future__ import annotations, annotations

from datetime import date
from typing import Optional

from fastui import components as c
from fastui.events import PageEvent
from pydantic import field_validator
from sqlmodel import Column, Field, JSON

from amherst.front.amui import Page, address_chooser_modal
from amherst.front import amui, css
from amherst.front.controller_abc import UI, UIState
# from amherst.models import HireWSubModels
from pawsupport.fastui_ps import fui
from pawsupport.convert import get_ordinal_suffix
from shipr.express import types as elt
from shipr.express.enums import ServiceCode


class HireState(UIState):
    boxes: int = 1
    ship_date: Optional[date] = Field(default_factory=date.today)
    ship_service: Optional[ServiceCode] = ServiceCode.EXPRESS24
    candidates: list[elt.AddressPF] = Field(default_factory=list, sa_column=Column(JSON))
    recipient_address: Optional[elt.AddressPF] = Field(default=None, sa_column=Column(JSON))
    recipient_contact: Optional[elt.ContactPF] = Field(default=None, sa_column=Column(JSON))

    @field_validator('ship_date', mode='after')
    def validate_ship_date(cls, v):
        return v if v >= date.today() else date.today()


class HireUI(UI):
    ...
    # # pfcom: AmShipper = Field(default_factory=AmShipper.from_env)
    # source_model: HireWSubModels
    # state: Optional[HireState] = None
    #
    # def initial_state(self):
    #     self.state.candidates = self.pfcom.get_candidates(
    #         self.source_model.delivery_address.postcode
    #     )
    #     self.state.recipient_address = self.pfcom.choose_hire_address(self.source_model)
    #     self.state.contact = elt.ContactPF.model_validate(self.source_model.contact_dict)
    #
    # async def get_components(self) -> list[c.AnyComponent]:
    #     return fui.Container.wrap(
    #         await self.address_section(),
    #         await self.details_section()
    #     )
    #
    # async def get_page(self) -> list[c.AnyComponent]:
    #     return Page.default_page(
    #         await self.get_components(),
    #         title="Hire Shipping"
    #     )
    #
    # # async def get_page(self, source_model: Hire) -> Page:
    # #     return Page(components=[await self.get_components(source_model=source_model)])
    #
    # async def address_section(self):
    #     async def amherst_address_col():
    #         split_add = self.source_model.delivery_address.address.strip().splitlines()
    #         return amui.Col.wrap(
    #             fui.Text(text=self.source_model.customer),
    #             *[fui.Text(text=_) for _ in split_add],
    #             wrap_inner=amui.Row
    #         )
    #
    #     async def address_buttons_div(outer_wrap=amui.Col, wrap_inner=amui.Row):
    #         ret = outer_wrap.wrap(
    #             fui.Text(text=f'Address score: {self.state.recipient_address.score}'),
    #             c.Button(text="Choose this address"),
    #             c.Button(text="Enter address manually", on_click=None),
    #             c.Button(
    #                 text='Choose a Different Address',
    #                 on_click=PageEvent(name='address-chooser')
    #             ),
    #             address_chooser_modal(self.state.candidates),
    #             wrap_inner=wrap_inner,
    #         )
    #         return ret
    #
    #     async def chosen_address_col():
    #         chosen = self.state.recipient_address
    #         return amui.Col.wrap(*fui.Text.all_text(chosen.address), wrap_inner=amui.Row)
    #
    #     return amui.Row(
    #         components=[
    #             await amherst_address_col(),
    #             await address_buttons_div(),
    #             await chosen_address_col()
    #         ]
    #     )
    #
    # async def details_section(self):
    #     async def boxes_btn():
    #         num_b = self.source_model.shipping.boxes
    #         return c.Button(text=f'{num_b} Boxes', on_click=None, class_name=css.BOXES_BTN)
    #
    #     async def date_btn():
    #         date_ = self.source_model.dates.send_out_date
    #         fstr = f'%A %d{get_ordinal_suffix(date_.day)} %B'
    #         text = f'{date_:{fstr}}'
    #         return c.Button(
    #             text=text,
    #             on_click=None,
    #         )
    #
    #     return amui.Row(
    #         components=[
    #             await date_btn(),
    #             await boxes_btn()
    #         ]
    #     )
