from __future__ import annotations

from datetime import date

from fastui import components as c
from loguru import logger

from amherst.models.hire import Hire
from amherst.models.shared import HireStatusEnum
from pawsupport import fastui_ps as fuis
from amherst.front.css import TITLE
from pawsupport.convert import get_ordinal_suffix
from pawsupport.fastui_ps import CSSEnum
from pawsupport.get_set import slug_or_none, title_or_name_val


# def get_headers1(header_names: list) -> c.Div:
#     headers = [c.Div(components=[c.Text(text=_)], class_name=HEAD) for _ in header_names]
#     head_row = fuis.Row(components=headers, row_class_name=HEAD)
#     return head_row

class CSSEnumAm(fuis.CSSEnum):
    STATUS_COL = "col-2"
    DATE_COL = "col-3"


class Row(fuis.Row):
    @classmethod
    def hire(cls, hire: Hire):
        try:
            components = [
                Col.date_col(hire.dates.send_out_date),
                Col.status_col(hire.status.status),
                Col.customer_col(hire.customer),
                Col.boxes_col(hire.shipping.boxes)
            ]
            row = cls(components=components, class_name=CSSEnum.ROW)
            return row
        except Exception as e:
            logger.error(e)
            raise

    @classmethod
    def headers(cls, header_names: list[str], class_name: str = CSSEnum.HEAD_ROW) -> 'Row':
        return super().headers(header_names, class_name)


class Col(fuis.Col):
    @classmethod
    def date(cls, col_date: date, class_name=CSSEnumAm.DATE_COL, text=None):
        if not text:
            fstr = f'%A %d{get_ordinal_suffix(col_date.day)} %B'
            text = f'{col_date:{fstr}}'
        comp = [c.Text(text=text)]
        return cls(components=comp, class_name=class_name)

    @classmethod
    def status(cls, status: HireStatusEnum, class_name=CSSEnumAm.STATUS_COL):
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
            class_name=CSSEnum.TITLE_COL,
            components=[
                fuis.LinkPR(),
            ],
        )


class Navbar(fuis.NavbarPR):
    @classmethod
    def hire(cls):
        return cls.from_routable(Hire)


class Page(fuis.PagePR):
    @classmethod
    def amherst(cls, components, title=None):
        try:
            page = super().default_page(
                title=title or "Amherst",
                navbar=Navbar.hire(),
                components=components,
                header_class=TITLE,
                # page_classname=PAGE,
            )
            return page
        except Exception as e:
            logger.error(e)
            raise
