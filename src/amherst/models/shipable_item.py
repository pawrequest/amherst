import datetime as dt
import typing as _t

import pydantic as _p
import pythoncom
import sqlmodel as sqm

import pycommence
from amherst.models import am_shared
from pycommence import cursor, pycmc_types
from shipr.models import base_item, pf_ext, pf_lists, pf_top

enum_map = {
    'Hire': am_shared.HireFields,
    'Sale': am_shared.SaleFields,
    'Customer': am_shared.CustomerFields,
}

AmherstFieldsEnum = am_shared.HireFields | am_shared.SaleFields | am_shared.CustomerFields


class ShipableItem(base_item.BaseItem):
    cmc_table_name: _t.Literal['Hire', 'Sale', 'Customer']
    record: dict[str, str] = sqm.Field(sa_column=sqm.Column(sqm.JSON))

    boxes: int | None = None
    ship_date: dt.date | None = None
    name: str | None = None
    input_address: pf_ext.AddressRecipient | None = None
    contact: pf_top.Contact | None = None
    fields_enum: type[AmherstFieldsEnum] = _p.Field(default=None, exclude=True)
    customer_record: dict[str, str] | None = None

    @_p.model_validator(mode='after')
    def get_values(self):
        self.fields_enum = enum_map.get(self.cmc_table_name)

        match self.cmc_table_name:
            case 'Hire' | 'Sale':
                business_name = self.record.get(self.fields_enum.CUSTOMER)
                if not self.customer_record:
                    with cursor.csr_context('Customer') as csr2:
                        pycmc = pycommence.PyCommence(csr=csr2)
                        self.customer_record = pycmc.one_record(business_name)

            case 'Customer':
                business_name = self.record.get(am_shared.CustomerFields.NAME)
                self.customer_record = self.record
            case _:
                raise ValueError(f'unknown table name: {self.cmc_table_name}')

        self.boxes = int(self.record.get(self.fields_enum.BOXES, 1))
        ship_date = self.record.get(self.fields_enum.SEND_OUT_DATE)
        self.ship_date = pycmc_types.get_cmc_date(ship_date) if ship_date else dt.date.today()
        phone = self.record.get(self.fields_enum.DELIVERY_TELEPHONE)
        email = self.record.get(self.fields_enum.DELIVERY_EMAIL)
        contact_name = self.record.get(self.fields_enum.DELIVERY_CONTACT)
        address_str = self.record.get(self.fields_enum.DELIVERY_ADDRESS)
        postcode = self.record.get(self.fields_enum.DELIVERY_POSTCODE)

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
