import datetime as dt
import typing as _ty

import pydantic as _p
import sqlmodel as sqm
from pycommence import api
from shipr.models import BaseItem, pf_ext, pf_lists, pf_shared, pf_top

from amherst.models import am_shared


class ShipableItem(BaseItem):
    cmc_table_name: str
    record: dict[str, str] = sqm.Field(sa_column=sqm.Column(sqm.JSON))
    initial_filter_array: _ty.ClassVar[api.FilterArray] = sqm.Field(
        default=am_shared.INITIAL_FILTER_ARRAY2,
        # sa_column=sqm.Column(sqm.JSON)
    )

    @_p.model_validator(mode='after')
    def get_values(self):
        match self.cmc_table_name:
            case 'Hire':
                self.boxes = int(self.record.get(am_shared.AmherstFields.BOXES))
                self.ship_date = api.get_cmc_date(
                    self.record.get(am_shared.AmherstFields.SEND_OUT_DATE)
                )
                phone = self.record.get(am_shared.AmherstFields.TELEPHONE)
            case 'Sale':
                self.boxes = 1
                self.ship_date = dt.date.today()
                phone = self.record.get(am_shared.AmherstFields.SALE_TELEPHONE)
            case _:
                raise ValueError(f'unknown table name: {self.cmc_table_name}')
        self.contact = pf_top.Contact(
            business_name=self.record.get(am_shared.AmherstFields.CUSTOMER),
            email_address=self.record.get(am_shared.AmherstFields.EMAIL),
            mobile_phone=phone,
            contact_name=self.record.get(am_shared.AmherstFields.CONTACT),
            notifications=pf_lists.Notifications(
                notification_type=[
                    pf_shared.NotificationType.EMAIL,
                    pf_shared.NotificationType.SMS_DOD,
                    pf_shared.NotificationType.SMS_ATTEMPT_DEL
                ]
            )
        )
        self.name = self.record.get(am_shared.AmherstFields.NAME)
        self.input_address = pf_ext.AddressRecipient(
            **am_shared.addr_lines_dict_am(
                self.record.get(am_shared.AmherstFields.ADDRESS)
            ),
            town='',
            postcode=self.record.get(am_shared.AmherstFields.POSTCODE),
        )

        return self


class Hire(BaseItem):
    cmc_table_name: str = 'Hire'
    record: dict[str, str]
    initial_filter_array: _ty.ClassVar[api.FilterArray] = sqm.Field(
        default=am_shared.INITIAL_FILTER_ARRAY2,
        # sa_column=sqm.Column(sqm.JSON)
    )

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
            v_date = api.get_cmc_date(v_str)
            if v_date > tod:
                return v_date
        return tod

    # @pyd.computed_field
    @property
    def input_address(self) -> pf_ext.AddressRecipient:
        return pf_ext.AddressRecipient(
            **am_shared.addr_lines_dict_am(self.record.get(am_shared.AmherstFields.ADDRESS)),
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
