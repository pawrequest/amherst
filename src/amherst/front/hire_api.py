from __future__ import annotations, annotations

from datetime import date, datetime
from typing import Optional

from fastui import components as c
from fastui.events import PageEvent
from pydantic import BaseModel, ConfigDict, Field, model_validator
from thefuzz import fuzz, process
from typing_extensions import Self

from amherst.shipping.pfcom import AmShipper
from amherst.front.amui import Containable, STYLESAm
from amherst.models import Hire
from pawsupport.fastui_ps import Container, STYLES
from shipr import types as elt
from amherst.front import amui
from pawsupport import fastui_ps as fui
from pawsupport.convert import get_ordinal_suffix


class UIState(BaseModel):
    pfcom: AmShipper
    hire: Hire
    boxes: int = Field(1)
    ship_date: Optional[date] = Field(None)

    candidates: Optional[elt.AddressCandidates] = None
    chosen_address: Optional[elt.AddressChoice] = None

    def get_addresses(self):
        self.candidates = self.pfcom.get_candidates(self.hire.delivery_address.postcode)
        self.chosen_address = self.pfcom.choose_hire_address(self.hire)

    @model_validator(mode='after')
    def validate_mod(self):
        tod = datetime.today().date()
        sd = self.ship_date or self.hire.dates.send_out_date
        self.ship_date = sd if sd >= tod else tod
        self.boxes = self.boxes or self.hire.shipping.boxes
        self.get_addresses()
        return self


class HireUI(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )
    hire: Hire
    pfcom: AmShipper
    state: Optional[UIState] = None

    async def hire_page(self):
        container = self.hire_container()
        page = Page.default_page(container, title="Address selection")
        return page


    @model_validator(mode='after')
    def validate_state(self) -> Self:
        if self.state is None:
            self.state = UIState(pfcom=self.pfcom, hire=self.hire)
        self.state.candidates = self.pfcom.get_candidates(self.hire.delivery_address.postcode)
        return self

    def date_ui(self, outer_wrap: Containable = amui.Col, class_name=STYLESAm.DATE_COL, text=None):
        date_ = self.hire.dates.send_out_date
        if not text:
            fstr = f'%A %d{get_ordinal_suffix(date_.day)} %B'
            text = f'{date_:{fstr}}'
        btn = [c.Button(
            text=text,
            on_click=None,
        )]
        return outer_wrap(components=btn, class_name=class_name)

    def address_commence(
            self,
            outer_wrap: Containable = amui.Col,
            inner_wrap: Containable = amui.Row
    ):
        addr_str = self.hire.delivery_address.address
        addr_txts = [fui.Text(text=_) for _ in addr_str.strip().splitlines()]
        return outer_wrap.wrap(
            fui.Text(text=self.hire.customer),
            *addr_txts,
            wrap_inner=inner_wrap,
        )

    def chosen_address(
            self,
            chosen: elt.AddressPF,
            outer_wrap: Containable = amui.Col,
            inner_wrap=amui.Row
    ):
        return outer_wrap.wrap(*fui.Text.all_text(chosen), wrap_inner=inner_wrap)

    def buttons(self, outer_wrap, score, wrap_inner=amui.Row):
        return outer_wrap.wrap(
            fui.Text(text=f'Address score: {score}'),
            c.Button(text="Choose this address"),
            c.Button(text="Enter address manually", on_click=None),
            c.Button(text='Choose a Different Address', on_click=PageEvent(name='address-chooser')),
            # address_chooser_modal(self.state.candidates),
            wrap_inner=wrap_inner,
        )

    def hire_address_compare(self, chosen, score, outer_wrap=amui.Row, inner_wrap=amui.Col):
        return outer_wrap(
            components=[
                self.address_commence(),
                self.buttons(inner_wrap, score),
                self.chosen_address(chosen)
            ]
        )

    def hire_container(self):
        address_rows = self.addressing_rows()
        date_boxes = self.get_boxes_date_ui()
        rows = [*address_rows, date_boxes]
        con = Container(components=rows)
        return con

    def addressing_rows(self):
        candidates = self.pfcom.get_candidates(self.hire.delivery_address.postcode)
        chosen, score = process.extractOne(
            self.hire.delivery_address.address,
            candidates,
            scorer=fuzz.token_sort_ratio
        )
        row1 = self.hire_address_compare(chosen, score)
        others = self.others_ui(amui.Row, candidates, amui.Col)
        rows = [row1, others]
        return rows

    def others_ui(
            self,
            outer_wrap: Containable,
            candidates: list[elt.AddressPF],
            inner_wrap=amui.Col
    ) -> Containable:
        res = outer_wrap.wrap(
            *[self.address_first_lines(can) for can in candidates],
            wrap_inner=inner_wrap
        )
        return res

    def address_first_lines(
            self,
            candidate: elt.AddressPF,
            outer_wrap: Containable = amui.Row
    ) -> Containable:
        contained = outer_wrap.wrap(
            fui.Text(text=f'{candidate.address_line1} {candidate.address_line2}')
        )
        return contained

    def boxes_ui(self, outer_wrap=amui.Col):
        num_b = self.hire.shipping.boxes
        btn = c.Button(text=f'{num_b} Boxes', on_click=None)
        return outer_wrap(components=[btn])

    def get_boxes_date_ui(self):
        date_ui = self.date_ui()
        boxes_ui = self.boxes_ui()
        return amui.Row.wrap(date_ui, boxes_ui)


# class HireSHipForm(BaseModel):
#
#     def get_smth(self):
#         return [
#             c.Button(text='Show Dynamic Modal', on_click=PageEvent(name='dynamic-modal')),
#             c.Modal(
#                 title='Dynamic Modal',
#                 body=[c.ServerLoad(path='/hire/dynamic-content')],
#                 footer=[
#                     c.Button(text='Close', on_click=PageEvent(name='dynamic-modal', clear=True)),
#                 ],
#                 open_trigger=PageEvent(name='dynamic-modal'),
#             ),
#         ]


# def address_chooser_modal(candidates: AddressCandidates) -> list[AnyComponent]:
#     return [
#         c.Modal(
#             title='Address Modal',
#             body=[
#                 address_chooser_buttons(candidates)
#             ],
#             footer=[
#                 c.Button(text='Close', on_click=PageEvent(name='address-chooser', clear=True)),
#             ],
#             open_trigger=PageEvent(name='address-chooser'),
#         ),
#     ]
#
#
# def address_chooser_buttons(candidates: AddressCandidates) -> list[AnyComponent]:
#     return [
#         c.Button(text=can.address_line1) for can in candidates.candidates
#     ]
class Page(fui.PagePR):
    class_name: str = STYLES.PAGE

    @classmethod
    async def hire_address(cls, hire_ui: HireUI):
        # candidates = pf_com.get_postcode_addresses(hire.delivery_address.postcode)
        # chosen, score = process.extractOne(hire.delivery_address.address, candidates, scorer=fuzz.token_sort_ratio)
        # row1 = hire_ui.hire_address_compare(amui.Row, hire, chosen, score)
        #
        # others = amui.others_ui(amui.Row, candidates, amui.Col)
        #
        # rows = [row1, others]
        #
        # con = Container(components=rows)

        con = hire_ui.hire_container()
        page = Page.default_page(con, title="Address selection")
        return page
