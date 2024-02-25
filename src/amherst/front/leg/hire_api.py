from __future__ import annotations, annotations

from typing import Optional

from fastui import components as c
from fastui.events import PageEvent
from pydantic import BaseModel, model_validator
from typing_extensions import Self

from amherst.back.routers import forms_rout as fr
from amherst.front.amui import address_chooser_modal, Page, address_first_lines
from amherst.front.ui_states import HireUIState
from amherst.shipping.pfcom import AmShipper
from amherst.front import amui, css
from amherst.models import Hire
from pawsupport.fastui_ps import Containable, fui
from pawsupport.convert import get_ordinal_suffix


def testing():
    return c.ModelForm(model=fr.AddressSelectReq, submit_url='/api/forms/select')


class HireUI(BaseModel):
    hire: Hire
    pfcom: AmShipper
    state: Optional[HireUIState] = None

    @model_validator(mode='after')
    def get_state(self) -> Self:
        self.state = self.state or HireUIState(pfcom=self.pfcom, hire=self.hire)
        return self

    async def hire_page2(self):
        return Page.default_page(testing(), title="Hire Shipping")

    async def hire_page(self):
        return Page.default_page(
            fui.Container.wrap(
                amui.Row(
                    components=[
                        self.cmc_address_div(),
                        self.address_buttons_div(),
                        self.chosen_address_div(),
                    ]
                ),
                amui.Row.wrap(
                    *[address_first_lines(can) for can in self.state.candidates],
                    wrap_inner=amui.Col
                ),
                amui.Row(components=[self.date_btn(), self.boxes_btn()])
            ),
            title="Hire Shipping"
        )

    def address_section(self):
        return amui.Row(
            components=[
                self.cmc_address_div(),
                self.address_buttons_div(),
                self.chosen_address_div()
            ]
        )

    def candidates_section(
            self,
    ) -> Containable:
        res = amui.Row.wrap(
            *[address_first_lines(can) for can in self.state.candidates],
            wrap_inner=amui.Col
        )
        return res

    # def details_section(self):
    #     return amui.Row.wrap(self.date_btn(), self.boxes_btn())

    def cmc_address_div(
            self,
    ):
        split_add = self.hire.delivery_address.address.strip().splitlines()
        split_add.append(self.hire.delivery_address.postcode)
        return amui.Col.wrap(
            fui.Text(text=self.hire.customer),
            *[fui.Text(text=_) for _ in split_add],
            wrap_inner=amui.Row
        )

    def chosen_address_div(
            self,
    ):
        chosen = self.state.chosen_address
        return amui.Col.wrap(*fui.Text.all_text(chosen.address), wrap_inner=amui.Row)

    def address_buttons_div(self, outer_wrap=amui.Col, wrap_inner=amui.Row):
        return outer_wrap.wrap(
            fui.Text(text=f'Address score: {self.state.chosen_address.score}'),
            c.Button(text="Choose this address"),
            c.Button(text="Enter address manually", on_click=None),
            c.Button(text='Choose a Different Address', on_click=PageEvent(name='address-chooser')),
            address_chooser_modal(self.state.candidates),
            wrap_inner=wrap_inner,
        )

    def details_div(self):
        return amui.Row(
            components=[
                self.date_btn(),
                self.boxes_btn()
            ]
        )

    def boxes_btn(self):
        num_b = self.hire.shipping.boxes
        return c.Button(text=f'{num_b} Boxes', on_click=None, class_name=css.BOXES_BTN)

    def date_btn(self):
        date_ = self.hire.dates.send_out_date
        fstr = f'%A %d{get_ordinal_suffix(date_.day)} %B'
        text = f'{date_:{fstr}}'
        return c.Button(
            text=text,
            on_click=None,
        )
