from __future__ import annotations

from datetime import date

from fastui import components as c, AnyComponent
from fastui.components import Text
from loguru import logger
from pydantic import BaseModel

from amherst.models.hire import Hire
from amherst.models.shared import HireStatusEnum
from amherst.shipping.parcelforce import choose_hire_address
from pawsupport import fastui_ps as fuis
from amherst.front.css import TITLE
from pawsupport.convert import get_ordinal_suffix
from pawsupport.fastui_ps import Container, STYLES, WrapMode
from pawsupport.get_set import slug_or_none, title_or_name_val
from shipr.el_combadge import PFCom


# def get_headers1(header_names: list) -> c.Div:
#     headers = [c.Div(components=[c.Text(text=_)], class_name=HEAD) for _ in header_names]
#     head_row = fuis.Row(components=headers, row_class_name=HEAD)
#     return head_row

class STYLESAm(fuis.STYLES):
    STATUS_COL = "col-2"
    DATE_COL = "col-3"


class Row(fuis.Row):
    @classmethod
    def hire(cls, hire: Hire):
        try:
            components = [
                Col.date(hire.dates.send_out_date),
                Col.status(hire.status.status),
                Col.customer(hire.customer),
                Col.boxes(hire.shipping.boxes)
            ]
            row = cls(components=components, class_name=STYLES.ROW)
            return row
        except Exception as e:
            logger.error(e)
            raise

    @classmethod
    def headers(cls, header_names: list[str], class_name: str = STYLES.HEAD_ROW) -> 'Row':
        return super().headers(header_names, class_name)


class Col(fuis.Col):
    @classmethod
    def date(cls, col_date: date, class_name=STYLESAm.DATE_COL, text=None):
        if not text:
            fstr = f'%A %d{get_ordinal_suffix(col_date.day)} %B'
            text = f'{col_date:{fstr}}'
        comp = [c.Text(text=text)]
        return cls(components=comp, class_name=class_name)

    @classmethod
    def status(cls, status: HireStatusEnum, class_name=STYLESAm.STATUS_COL):
        text = status
        comp = [c.Text(text=text)]
        return fuis.Col(components=comp, class_name=class_name)

    @classmethod
    def customer(cls, customer: str, class_name=""):
        text = customer
        comp = [c.Text(text=text)]
        return fuis.Col(components=comp, class_name=class_name)

    @classmethod
    def boxes(cls, boxes: int, class_name="col-1"):
        text = f"{boxes} {'box' if boxes == 1 else 'boxes'}"
        comp = [c.Text(text=text)]
        return fuis.Col(components=comp, class_name=class_name)

    @classmethod
    def title(cls, obj) -> fuis.Col:
        url = slug_or_none(obj)
        title = title_or_name_val(obj)
        return cls(
            class_name=STYLES.TITLE_COL,
            components=[
                fuis.LinkPR(),
            ],
        )

    @classmethod
    def all_text(cls, obj: BaseModel):
        txts = [Text(text=_) for _ in list(obj.model_dump().values()) if _]

        return cls.wrap(*txts, wrap_mode=WrapMode.NESTED, wrap_inner=Row, wrap_outer=Col)


class Navbar(fuis.NavbarPR):
    @classmethod
    def hire(cls):
        return cls.from_routable(Hire)


class Page(fuis.PagePR):

    @classmethod
    async def hire_address(cls, hire: Hire, pf_com: PFCom):
        chosen_add, score = choose_hire_address(hire, pf_com)
        am_address_col = Col.all_text(hire.delivery_address)
        chosen_add_col = Col.all_text(chosen_add)
        buttons_col = Col.wrap(
            c.Text(text=f'Address score: {score}'),
            c.Button(text="Choose this address", ),
            c.Button(text="Enter address manually", on_click=None),
            wrap_mode=WrapMode.NESTED,
            wrap_inner=Row,
            wrap_outer=Col
        )
        cont = Container.wrap(am_address_col,buttons_col, chosen_add_col, wrap_mode=WrapMode.NESTED, wrap_inner=Col, wrap_outer=Row)
        page = Page.default_page(cont)
        return page


