from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING, Union

from fastui import components as c

from shipr.express.types import AddressPF

if TYPE_CHECKING:
    from amherst.front import ContainableType
from amherst.models.hire import Hire
from pawsupport import fastui_ps as fui
from pawsupport.convert import get_ordinal_suffix
from pawsupport.fastui_ps import STYLES


class STYLESAm(fui.STYLES):
    STATUS_COL = "col-2"
    DATE_COL = "col-3"


class Row(fui.Row):
    class_name: str = STYLES.ROW

    @classmethod
    def headers(cls, header_names: list[str], class_name: str = STYLES.HEAD_ROW) -> 'Row':
        return super().headers(header_names, class_name)


class Col(fui.Col):
    class_name: str = STYLES.COL


class Navbar(fui.NavbarPR):
    @classmethod
    def hire(cls):
        return cls.from_routable(Hire)


def date(cls, col_date: date, class_name=STYLESAm.DATE_COL, text=None):
    if not text:
        fstr = f'%A %d{get_ordinal_suffix(col_date.day)} %B'
        text = f'{col_date:{fstr}}'
    comp = [fui.Text(text=text)]
    return cls(components=comp, class_name=class_name)


def hire_address_am(cls, hire: Hire, wrap_inner=Row):
    addr_str = hire.delivery_address.address
    addr_txts = [fui.Text(text=_) for _ in addr_str.strip().splitlines()]
    return cls.wrap(
        fui.Text(text=hire.customer),
        *addr_txts,
        wrap_inner=wrap_inner,
    )


def chosen_address_am(cls, chosen, wrap_inner=Row):
    return cls.wrap(*fui.Text.all_text(chosen), wrap_inner=wrap_inner)


def buttons(cls, score, wrap_inner=Row):
    return cls.wrap(
        fui.Text(text=f'Address score: {score}'),
        c.Button(text="Choose this address"),
        c.Button(text="Enter address manually", on_click=None),
        wrap_inner=wrap_inner,
    )


def hire_address_compare(cls, hire: Hire, chosen, score, wrap_inner=Col):
    return cls(
        components=[
            hire_address_am(wrap_inner, hire),
            buttons(wrap_inner, score),
            chosen_address_am(wrap_inner, chosen)
        ]
    )


def others_ui(
        cls: type[ContainableType],
        candidates: list[AddressPF],
        wrap_inner=Col
) -> ContainableType:
    res = cls.wrap(
        *[address_first_lines(cls, can) for can in candidates],
        wrap_inner=wrap_inner
    )
    return res
    # inner = [fui.Text.all_text(_) for _ in candidates]
    # inn = [cls.list_of(_) for _ in inner]
    # others_inner = [cls.wrap(*_) for _ in txts]
    # ret = cls.wrap(*inn, wrap_inner=wrap_inner)
    # return ret


def address_first_lines(
        cls: type[ContainableType],
        candidate: AddressPF,
        # wrap_inner: type[Containable],
) -> ContainableType:
    contained = cls.wrap(fui.Text(text=f'{candidate.address_line1} {candidate.address_line2}'))
    return contained


Containable = Union[type[Row], type[Col]]
