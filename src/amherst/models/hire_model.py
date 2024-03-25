import datetime as dt
import typing as _ty

import pydantic as _p
import sqlmodel as sqm

from amherst.models import am_shared
from pycommence import api
from shipr.models import base_item, pf_ext, pf_lists, pf_top


class ShipableItem(base_item.BaseItem):
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
                fields_enum = am_shared.HireFields
                business_name = self.record.get(am_shared.HireFields.CUSTOMER)
            case 'Sale':
                fields_enum = am_shared.SaleFields
                business_name = self.record.get(am_shared.HireFields.CUSTOMER)
            case 'Customer':
                fields_enum = am_shared.CustomerFields
                business_name = self.record.get(am_shared.CustomerFields.NAME)
            case _:
                raise ValueError(f'unknown table name: {self.cmc_table_name}')

        self.boxes = int(self.record.get(fields_enum.BOXES, 1))
        shippy = self.record.get(fields_enum.SEND_OUT_DATE)
        self.ship_date = api.get_cmc_date(shippy) if shippy else dt.date.today()
        phone = self.record.get(fields_enum.DELIVERY_TELEPHONE)
        email = self.record.get(fields_enum.DELIVERY_EMAIL)
        contact_name = self.record.get(fields_enum.DELIVERY_CONTACT)
        address_str = self.record.get(fields_enum.DELIVERY_ADDRESS)
        postcode = self.record.get(fields_enum.DELIVERY_POSTCODE)

        self.contact = pf_top.Contact(
            business_name=business_name,
            email_address=email,
            mobile_phone=phone,
            contact_name=contact_name,
            notifications=pf_lists.RecipientNotifications.standard_recip(),
        )
        self.name = self.record.get(am_shared.HireFields.NAME)
        self.input_address = pf_ext.AddressRecipient(
            **am_shared.addr_lines_dict_am(
                address_str
            ),
            town='',
            postcode=postcode,
        )

        return self

