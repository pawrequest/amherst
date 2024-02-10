from __future__ import annotations

from typing import Sequence, Union

from amherst.models.hire import Hire
from fastui import components as c
from fastui.events import GoToEvent
from loguru import logger
from pawsupport.fastui_ps import fastui_support as fuis
from pawsupport.fastui_ps.fastui_support import default_page
from pawsupport.get_set import slug_or_none, title_or_name_val
from amherst.front.css import HEAD, PLAY_COL, TITLE, TITLE_COL


def get_headers(header_names: list) -> c.Div:
    headers = [c.Div(components=[c.Text(text=_)], class_name=HEAD) for _ in header_names]
    head_row = fuis.Row(components=headers, class_name=HEAD)
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
    return fuis.Col(components=[clink], class_name=class_name)


def title_column(obj) -> fuis.Col:
    url = slug_or_none(obj)
    title = title_or_name_val(obj)
    return fuis.Col(
        class_name=TITLE_COL,
        components=[
            ui_link(title, url),
        ],
    )


def play_column(url) -> fuis.Col:
    res = fuis.Col(
        class_name=PLAY_COL,
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
        row = fuis.Row(
            components=[
                c.Text(text=f'{hire.dates.send_out_date:%d-%m}'),
                c.Text(text=hire.status.status),
                c.Text(text=hire.customer),
            ],
        )
        return row
    except Exception as e:
        logger.error(e)
        raise
