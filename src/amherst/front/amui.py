from __future__ import annotations

from datetime import date
from enum import Enum, auto

import fastui.class_name as _class_name
from fastui import components as c

from pawdantic.pawui import styles
from shipr.models import pf_ext


class Page(c.Page):
    @classmethod
    def default_page(
            cls,
            *components: c.AnyComponent,
            title: str = 'Amherst',
            navbar=None,
            footer=None,
            header_class: _class_name.ClassNameField = None,
            class_name: _class_name.ClassNameField = None,
            contained=False,
    ) -> list[c.AnyComponent]:
        return super().default_page(
            *components,
            title=title,
            navbar=navbar,
            footer=footer,
            header_class=header_class,
            class_name=class_name,
            contained=contained,
        )


def address_first_lines(
        candidate: pf_ext.AddressRecipient,
        class_name: _class_name.ClassName = styles.ROW_STYLE,
):
    return c.Div.wrap(
        c.Text(text=f'{candidate.address_line1} {candidate.address_line2}'),
        class_name=class_name
    )


def get_ordinal_suffix(day: int) -> str:
    return {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th') if day not in (11, 12, 13) else 'th'


def date_string(date_: date) -> str:
    fstr = f'%A %#d{get_ordinal_suffix(date_.day)} %B'
    return f'{date_:{fstr}}'


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
