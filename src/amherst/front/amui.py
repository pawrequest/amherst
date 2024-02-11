from __future__ import annotations

from typing import Sequence, Union

from amherst.models.hire import Hire
from amherst.models.shared import HireStatusEnum
from fastui import components as c
from fastui.events import GoToEvent
from loguru import logger
from pawsupport.convert import get_ordinal_suffix
from pawsupport.fastui_ps import fastui_support as fuis
from pawsupport.fastui_ps.fastui_support import default_page
from pawsupport.get_set import slug_or_none, title_or_name_val
from amherst.front.css import HEAD, PLAY_COL, TITLE, TITLE_COL
from datetime import date

def get_headers(header_names: list) -> c.Div:
    headers = [c.Div(components=[c.Text(text=_)], class_name=HEAD) for _ in header_names]
    head_row = fuis.Row(components=headers, row_class_name=HEAD)
    return head_row


def objects_col(objects: Sequence, class_name_int="", class_name_ext="") -> c.Div:
    try:
        if not objects:
            return fuis.empty_div(col=True)
        rows = [object_col_one(_, class_name_int) for _ in objects]
        col = fuis.Col(components=rows)
        return col
    except Exception as e:
        logger.error(e)


def object_col_one(obj, class_name="") -> Union[c.Div, c.Link]:
    if not obj:
        return fuis.empty_div(col=True)
    clink = ui_link(title_or_name_val(obj), slug_or_none(obj))
    return fuis.Col(components=[clink], col_class=class_name)


def title_column(obj) -> fuis.Col:
    url = slug_or_none(obj)
    title = title_or_name_val(obj)
    return fuis.Col(
        col_class=TITLE_COL,
        components=[
            ui_link(title, url),
        ],
    )


def play_column(url) -> fuis.Col:
    res = fuis.Col(
        col_class=PLAY_COL,
        components=[
            c.Link(
                components=[c.Text(text="Play")],
                on_click=GoToEvent(url=url),
            ),
        ],
    )
    return res


def ui_link(title, url, on_click=None, class_name="") -> c.Link:
    on_click = on_click or GoToEvent(url=url)
    link = c.Link(components=[c.Text(text=title)], on_click=on_click, class_name=class_name)
    return link


def am_navbar():
    return fuis.nav_bar_from_routable([Hire])


def am_default_page(components, title=None):
    try:
        page = default_page(
            title=title or "Amherst",
            navbar=am_navbar(),
            components=components,
            header_class=TITLE,
            # page_classname=PAGE,
        )
        return page
    except Exception as e:
        logger.error(e)
        raise


def hire_row(hire: Hire):
    try:
        components = [
            date_col(hire.dates.send_out_date),
            status_col(hire.status.status),
            customer_col(hire.customer),
            boxes_col(hire.shipping.boxes)
        ]
        row = fuis.Row(components=components, sub_cols=False)
        return row
    except Exception as e:
        logger.error(e)
        raise


def date_col(col_date: date, class_name="col-3", text=None):
    if not text:
        fstr = f'%A %d{get_ordinal_suffix(col_date.day)} %B'
        text = f'{col_date:{fstr}}'
    comp = [c.Text(text=text)]
    return fuis.Col(components=comp, col_class=class_name)


def status_col(status: HireStatusEnum, class_name="col-2"):
    text = status
    comp = [c.Text(text=text)]
    return fuis.Col(components=comp, col_class=class_name)


def customer_col(customer: str, class_name=""):
    text = customer
    comp = [c.Text(text=text)]
    return fuis.Col(components=comp, col_class=class_name)


def boxes_col(boxes: int, class_name="col-1"):
    text = f"{boxes} {'box' if boxes == 1 else 'boxes'}"
    comp = [c.Text(text=text)]
    return fuis.Col(components=comp, col_class=class_name)
