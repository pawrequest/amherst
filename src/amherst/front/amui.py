from __future__ import annotations

from datetime import date

import fastui.class_name as _class_name
from fastui import builders, styles
from fastui import components as c
from pawsupport.convert import get_ordinal_suffix
from shipr.models import pf_ext, pf_top


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
    return c.Div.wrap(c.Text(text=f'{candidate.address_line1} {candidate.address_line2}'), class_name=class_name)


def date_string(date_: date) -> str:
    fstr = f'%A %#d{get_ordinal_suffix(date_.day)} %B'
    return f'{date_:{fstr}}'


async def address_n_contact_col(
    address: pf_ext.AddressRecipient,
    contact: pf_top.Contact,
    title_prefix: str = '',
) -> c.Div:
    return c.Div.wrap(
        *builders.all_text(contact, title=f'{title_prefix}Contact', class_name=styles.ROW_STYLE),
        *builders.all_text(address, title=f'{title_prefix}Address', class_name=styles.ROW_STYLE),
        class_name=styles.COL_STYLE,
        inner_class_name=styles.ROW_STYLE,
    )
