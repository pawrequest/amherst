from __future__ import annotations

from datetime import date, timedelta
from enum import Enum, auto

from fastui import AnyComponent, components as c
from pydantic import condate

from amherst.front import css, amui


def date_range_type():
    tod = date.today()
    end = tod + timedelta(days=7)
    return condate(ge=tod, le=end)


class BoxesEnum(str, Enum):
    one = auto()
    two = auto()
    three = auto()
    four = auto()
    five = auto()
    six = auto()
    seven = auto()
    eight = auto()
    nine = auto()
    ten = auto()


async def page_w_alerts(
    components: list[AnyComponent],
    title: str = "",
    navbar=None,
    footer=None,
    class_name=css.PAGE,
    alerts=None,
) -> list[AnyComponent]:
    alert_texts = [amui.Text(text=al.message) for al in alerts]
    components_ = [
        *((*alert_texts,) if alert_texts else ()),
        *components,
    ]
    return [
        c.PageTitle(text=f"PawRequest dev - {title}" if title else ""),
        *((navbar,) if navbar else ()),
        c.Page(
            components=components_,
            class_name=class_name,
        ),
        *((footer,) if footer else ()),
    ]
