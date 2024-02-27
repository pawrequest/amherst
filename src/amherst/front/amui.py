from __future__ import annotations

from pawsupport.convert import get_ordinal_suffix
from pawsupport.fastui_ps import Containable, fui
from amherst.front import css
from shipr.models import pf_types as elt


class Container(fui.Container):
    class_name: str = css.CONTAINER


class Link(fui.Link):
    ...


class Row(fui.Row):
    class_name: str = css.ROW

    @classmethod
    def headers(cls, header_names: list[str], class_name: str = css.HEAD_ROW) -> 'Row':
        return super().headers(header_names, class_name)


class Col(fui.Col):
    class_name: str = css.COL


class Navbar(fui.NavbarPR):
    ...
    # @classmethod
    # def hire(cls):
    #     return cls.from_routable(Hire)


class Page(fui.PagePR):
    class_name: str = css.PAGE


def address_first_lines(
        candidate: elt.AddressPF,
        outer_wrap: Containable = Row
) -> Containable:
    contained = outer_wrap.wrap(
        fui.Text(text=f'{candidate.address_line1} {candidate.address_line2}')
    )
    return contained


async def date_string(date_):
    fstr = f'%A %#d{get_ordinal_suffix(date_.day)} %B'
    text = f'{date_:{fstr}}'
    return text


async def address_col(address: elt.AddressPF, wrap_in=None):
    txts = fui.Text.all_text(address)
    if wrap_in:
        return wrap_in.wrap(*txts, wrap_inner=Row)
    return txts
