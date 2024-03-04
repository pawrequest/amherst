# from __future__ import annotations

import datetime as dt
import typing as _ty

import sqlmodel as sqm

import pycommence
import pycommence as cmc
import pycommence.wrapper
from amherst.models import am_shared
from shipr.models import (
    pf_ext,
    pf_shared,
    pf_top,
)

# if _ty.TYPE_CHECKING:
#     pass


class Hire(pf_shared.BasePFType):
    cmc_table_name: _ty.ClassVar[str] = 'Hire'
    initial_filter_array: _ty.ClassVar[cmc.FilterArray] = sqm.Field(
        default=am_shared.INITIAL_FILTER_ARRAY2,
        # sa_column=sqm.Column(sqm.JSON)
    )

    record: dict[str, str]

    # @pyd.computed_field
    @property
    def boxes(self) -> int:
        return int(self.record.get(am_shared.AmherstFields.BOXES))

    # @pyd.computed_field
    @property
    def name(self) -> str:
        return self.record.get(am_shared.AmherstFields.NAME)

    # @pyd.computed_field
    @property
    def ship_date(self) -> dt.date:
        """uses cmc cannonical format yyyymmdd"""
        tod = dt.date.today()
        if v_str := self.record.get(am_shared.AmherstFields.SEND_OUT_DATE):
            v_date = cmc.get_cmc_date(v_str)
            if v_date > tod:
                return v_date
        return tod

    # @pyd.computed_field
    @property
    def input_address(self) -> pf_ext.AddressRecipient:
        return pf_ext.AddressRecipient(
            **addr_lines_dict_am(self.record.get(am_shared.AmherstFields.ADDRESS)),
            town='',
            postcode=self.record.get(am_shared.AmherstFields.POSTCODE),
        )

    # @pyd.computed_field
    @property
    def contact(self) -> pf_top.Contact:
        return pf_top.Contact(
            business_name=self.record.get(am_shared.AmherstFields.CUSTOMER),
            email_address=self.record.get(am_shared.AmherstFields.EMAIL),
            mobile_phone=self.record.get(am_shared.AmherstFields.TELEPHONE),
            contact_name=self.record.get(am_shared.AmherstFields.CONTACT),
        )


def addr_lines_dict_am(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
    return {f'address_line{num}': line for num, line in enumerate(addr_lines, start=1)}


#
