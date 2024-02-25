from __future__ import annotations

from fastui import components as c
from fastui.events import GoToEvent, PageEvent

from pawsupport.fastui_ps import Containable, fui
from amherst.front import css
from shipr.express import types as elt


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


def address_chooser_modal(candidates: list[elt.AddressPF]) -> c.Modal:
    return c.Modal(
        title='Address Modal',
        body=address_chooser_buttons(candidates),
        footer=[
            c.Button(text='Close', on_click=PageEvent(name='address-chooser', clear=True)),
        ],
        open_trigger=PageEvent(name='address-chooser'),
    )


def address_chooser_buttons(candidates: list[elt.AddressPF]) -> list[c.AnyComponent]:
    ret = [
        c.Button(
            text=can.address_line1, on_click=GoToEvent(url='/hire', query=can.model_dump())
        ) for can in candidates
    ]
    return ret


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
