from __future__ import annotations

from datetime import date, timedelta
from enum import Enum, auto

from fastui import AnyComponent, components as c
from pydantic import condate

from amherst.front import amui, css


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

    al_row = amui.Row(
        components=[amui.Text(text=al.message) for al in alerts]
    ) if alerts else amui.Row.empty()

    # alert_texts = [amui.Text(text=al.message) for al in alerts] if alerts else []
    # al = *((*alert_texts,) if alert_texts else ()),
    #
    # alert_row = amui.Row.wrap(*alert_texts)
    components_ = [
        # *((*alert_texts,) if alert_texts else ()),
        al_row,
        *components,
    ]
    contained = [amui.Container(components=components_)]
    return [
        c.PageTitle(text=f"PawRequest dev - {title}" if title else ""),
        *((navbar,) if navbar else ()),
        c.Page(
            components=contained,
            class_name=class_name,
        ),
        *((footer,) if footer else ()),
    ]
