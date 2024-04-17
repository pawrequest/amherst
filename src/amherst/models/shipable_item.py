import datetime as dt

import pydantic as _p
import sqlmodel as sqm
from loguru import logger

import pycommence
from amherst.am_types import AmherstFieldsEnumType, AmherstTableName
from amherst.models import am_shared
from pycommence import pycmc_types
from shipr.models import base_item, pf_ext, pf_lists, pf_top


# enum_map = {
#     'Hire': am_shared.HireFields,
#     'Sale': am_shared.SaleFields,
#     'Customer': am_shared.CustomerFields,
# }


class ShipableItem(base_item.BaseItem):
    """A shipable item

    Attributes:
        cmc_table_name (AmherstTableName): The name of the table in Commence
        record (dict[str, str]): The record from Commence

        boxes (int | None): The number of boxes
        ship_date (dt.date | None): The date to ship
        name (str | None): The name of the item
        input_address (pf_ext.AddressRecipient | None): The address to ship to
        contact (pf_top.Contact | None): The contact to ship to
        fields_enum (type[AmherstFieldsEnumType]): The fields enum for the table
        customer_record (dict[str, str] | None): The customer record

    """
    cmc_table_name: AmherstTableName
    record: dict[str, str] = sqm.Field(sa_column=sqm.Column(sqm.JSON))

    boxes: int | None = None
    ship_date: dt.date | None = None
    name: str | None = None
    input_address: pf_ext.AddressRecipient | None = None
    contact: pf_top.Contact | None = None
    fields_enum: type[AmherstFieldsEnumType] = _p.Field(default=None, exclude=True)
    customer_record: dict[str, str] | None = _p.Field(default=None, sa_column=sqm.Column(sqm.JSON))

    @_p.model_validator(mode='after')
    def get_values(self):
        self.fields_enum = self.fields_enum or getattr(am_shared, self.cmc_table_name + 'Fields')

        match self.cmc_table_name:
            case 'Hire' | 'Sale':
                business_name = self.record.get(self.fields_enum.CUSTOMER)
                self.customer_record = self.customer_record or get_customer_record(
                    customer=business_name
                )

            case 'Customer':
                business_name = self.record.get(am_shared.CustomerFields.NAME)
                self.customer_record = self.record

            case _:
                raise ValueError(f'unknown table name: {self.cmc_table_name}')

        self.boxes = int(self.record.get(self.fields_enum.BOXES, 1))
        ship_date = self.record.get(self.fields_enum.SEND_OUT_DATE)
        self.ship_date = pycmc_types.get_cmc_date(ship_date) if ship_date else dt.date.today()
        phone = self.record.get(self.fields_enum.DELIVERY_TELEPHONE)
        email = (self.record.get(self.fields_enum.DELIVERY_EMAIL)
                 or self.customer_record.get(self.fields_enum.PRIMARY_EMAIL))
        contact_name = self.record.get(self.fields_enum.DELIVERY_CONTACT)
        postcode = self.record.get(self.fields_enum.DELIVERY_POSTCODE)
        address_str = (self.record.get(self.fields_enum.DELIVERY_ADDRESS)
                       or self.customer_record.get(am_shared.CustomerFields.DELIVERY_ADDRESS)
                       or self.customer_record.get(am_shared.CustomerFields.INVOICE_ADDRESS)
                       )

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


class ShipableRecor(ShipableItem):
    ...


def get_customer_record(customer: str) -> dict[str, str]:
    """Get a customer record from `:class:PyCommence`"""
    logger.debug(f'Getting customer record for {customer}')
    logger.warning('not initialising comtypes what say ye thread gods?')
    # comtypes.CoInitialize()
    py_cmc = pycommence.PyCommence.from_table_name(table_name='Customer')
    rec = py_cmc.one_record(customer)
    # comtypes.CoUninitialize()
    return rec
