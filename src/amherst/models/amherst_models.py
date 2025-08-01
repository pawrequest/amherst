from abc import ABC
from datetime import date
from os import PathLike

from loguru import logger
from pycommence.pycmc_types import RowInfo
from pydantic import BaseModel, ConfigDict, Field, model_validator, field_validator
from shipaw.models.pf_models import AddressBase, AddressSender
from shipaw.models.pf_msg import ShipmentResponse
from shipaw.models.pf_shipment import Shipment, ShipmentAwayDropoff, ShipmentAwayCollection
from shipaw.models.pf_top import CollectionInfo, Contact, ContactSender
from shipaw.ship_types import ShipmentType, limit_daterange_no_weekends

from amherst.models.commence_adaptors import AM_DATE, CategoryName, HireAliases, HireStatus, SaleStatus


class AmherstShipableBase(BaseModel, ABC):
    model_config = ConfigDict(
        populate_by_name=True,
        use_enum_values=True,
    )
    row_info: RowInfo
    # amherst common fieldnames fields
    name: str = Field(..., alias='Name')

    tracking_numbers: str = Field('', alias='Tracking Numbers')

    # mandatory fields
    customer_name: str
    delivery_contact_name: str
    delivery_contact_business: str
    delivery_contact_phone: str
    delivery_contact_email: str
    delivery_address_str: str
    delivery_address_pc: str

    # optional fields with default
    send_date: AM_DATE = date.today()
    boxes: int = 1

    # parcelforce objects
    _delivery_contact: Contact | None = None
    _delivery_address: AddressBase | None = None
    # todo addressBase could be AddressRecipient for outbound, and AddressSender for inbound, to allow longer strings

    @field_validator('send_date', mode='after')
    def validate_send_date(cls, v: AM_DATE) -> date:
        if v is None or v < date.today():
            return date.today()
        return v

    @property
    def delivery_contact(self) -> Contact:
        if self._delivery_contact is None:
            self._delivery_contact = Contact(
                contact_name=self.delivery_contact_name,
                business_name=self.delivery_contact_business,
                mobile_phone=self.delivery_contact_phone,
                email_address=self.delivery_contact_email,
            )
        return self._delivery_contact

    @property
    def delivery_address(self):
        if not self._delivery_address:
            self._delivery_address = AddressBase(
                **split_addr_str(self.delivery_address_str),
                postcode=self.delivery_address_pc,
            )
        return self._delivery_address

    def shipment_dict(self):
        return {
            'recipient_address': self.delivery_address.model_dump(),
            'recipient_contact': self.delivery_contact.model_dump(),
            'total_number_of_parcels': self.boxes,
            'shipping_date': limit_daterange_no_weekends(self.send_date) or date.today(),
            **shipment_refs_dict_from_str(self.customer_name),
        }

    def shipment(self):
        return Shipment.model_validate(self.shipment_dict())


class AmherstCustomer(AmherstShipableBase):
    # mandatory overrides
    delivery_contact_name: str = Field(..., alias='Deliv Contact')
    delivery_contact_business: str = Field(..., alias='Deliv Name')
    delivery_contact_phone: str = Field(..., alias='Deliv Telephone')
    delivery_contact_email: str = Field(..., alias='Deliv Email')
    delivery_address_str: str = Field(..., alias='Deliv Address')
    delivery_address_pc: str = Field(..., alias='Deliv Postcode')

    # optional overrides
    customer_name: str = Field(..., alias='Name')
    send_date: AM_DATE = date.today()

    # customer fields
    invoice_email: str = Field('', alias='Invoice Email')
    accounts_email: str = Field('', alias='Accounts Email')
    hires: str = ''
    sales: str = ''


class AmherstOrderBase(AmherstShipableBase, ABC):
    # mandatory overrides
    customer_name: str = Field(..., alias='To Customer')
    delivery_contact_name: str = Field(..., alias='Delivery Contact')
    delivery_contact_business: str = Field(..., alias='Delivery Name')
    delivery_contact_phone: str = Field(..., alias='Delivery Telephone')
    delivery_contact_email: str = Field(..., alias='Delivery Email')
    delivery_address_str: str = Field(..., alias='Delivery Address')
    delivery_address_pc: str = Field(..., alias='Delivery Postcode')

    # order fields common
    status: str = Field(..., alias='Status')
    arranged_in: str = Field('', alias='Pickup Arranged')
    arranged_out: str = Field('', alias='DB label printed')
    invoice: PathLike = Field('', alias='Invoice')

    # order fields optional
    date_sent: AM_DATE | None = None
    booking_date: AM_DATE | None = None


class AmherstSale(AmherstOrderBase):
    # mandatory overrides master
    # category:CategoryName = 'Sale'

    # optional overrides master
    send_date: date = date.today()
    #        # return self.booking_date or date.today()

    # mandatory overrides order
    delivery_method: str = Field('', alias='Delivery Method')

    # optional overrides order
    status: SaleStatus = Field(..., alias='Status')
    booking_date: AM_DATE = Field(date.today(), alias='Date Ordered')
    date_sent: AM_DATE = Field(None, alias='Date Sent')

    # sale fields
    lost_equipment: str = Field('', alias='Lost Equipment')
    invoice_terms: str = Field('', alias='Invoice Terms')
    purchase_order: str = Field('', alias='Purchase Order')
    items_ordered: str = Field('', alias='Items Ordered')
    serial_numbers: str = Field('', alias='Serial Numbers')
    delivery_notes: str = Field('', alias='Delivery Notes')
    notes: str = Field('', alias='Notes')


class AmherstTrial(AmherstOrderBase):
    # category:CategoryName = CategoryName.Trial
    customer_name: str = Field(..., alias='Involves Customer')
    delivery_contact_name: str = Field(..., alias='Trial Contact')
    delivery_contact_business: str = Field(..., alias='Trial Name')
    delivery_contact_phone: str = Field(..., alias='Trial Telephone')
    delivery_contact_email: str = Field(..., alias='Trial Email')
    delivery_address_str: str = Field(..., alias='Trial Address')
    delivery_address_pc: str = Field(..., alias='Trial Postcode')
    tracking_numbers: str = Field('', alias='Tracking Numbers')

    invoice: str = Field('', alias='Our Invoice')


class AmherstHire(AmherstOrderBase):
    # optional overrides master
    boxes: int = Field(1, alias='Boxes')
    delivery_contact_phone: str = Field(..., alias='Delivery Tel')
    send_date: AM_DATE = Field(date.today(), alias='Send Out Date')

    delivery_method: str = Field(..., alias='Send Method')

    # optional overrides order
    status: HireStatus = Field(..., alias='Status')
    date_sent: AM_DATE = Field(None, alias='Actual Send Date')
    booking_date: AM_DATE = Field(date.today(), alias='Booked Date')

    # hire fields
    missing_kit_str: str = Field('', alias='Missing Kit')
    due_back_date: AM_DATE = Field(..., alias=HireAliases.DUE_BACK_DATE)

    track_out: str = Field('', alias='Track Outbound')
    track_in: str = Field('', alias='Track Inbound')


AMHERST_ORDER_MODELS = AmherstHire | AmherstSale | AmherstTrial
AMHERST_TABLE_MODELS = AMHERST_ORDER_MODELS | AmherstCustomer
SHIPMENT_TYPES = Shipment | ShipmentAwayDropoff | ShipmentAwayCollection


def shipment_refs_dict_from_str(ref_str: str, max_len: int = 24) -> dict[str, str]:
    reference_numbers = {}

    for i in range(1, 6):
        start_index = (i - 1) * max_len
        end_index = i * max_len
        if start_index < len(ref_str):
            reference_numbers[f'reference_number{i}'] = ref_str[start_index:end_index]
        else:
            break
    return reference_numbers


def address_from_str(add_str: str, postcode: str) -> dict:
    return {
        **split_addr_str(add_str),
        'postcode': postcode,
    }


def split_addr_str(address: str) -> dict[str, str]:
    addr_lines = address.splitlines()
    town = addr_lines.pop() if len(addr_lines) > 1 else ''

    if len(addr_lines) < 3:
        addr_lines.extend([''] * (3 - len(addr_lines)))
    elif len(addr_lines) > 3:
        addr_lines[2] = ','.join(addr_lines[2:])
        addr_lines = addr_lines[:3]

    used_lines = [_ for _ in addr_lines if _]
    return {f'address_line{num}': line for num, line in enumerate(used_lines, start=1)} | {'town': town}


# class AmherstAddress(BaseModel):
#     address_str: str
#     postcode: str
#
#     def address_dict(self) -> dict:
#         return {
#             **split_addr_str(self.address_str),
#             'postcode': self.postcode,
#         }
#
#     def pf_address_base(self) -> AddressBase:
#         return AddressBase.model_validate(self, from_attributes=True)


# class AmherstContact(BaseModel):
#     contact_name: str
#     business_name: str
#     mobile_phone: str
#     email_address: str
#
#     def pf_contact(self) -> Contact:
#         return Contact.model_validate(self, from_attributes=True)


# class AmherstDeliveryAddress(AmherstAddress):
#     address_str: str = Field(..., alias='Delivery Address')
#     postcode: str = Field(..., alias='Delivery Postcode')


# class AmherstDeliveryContact(AmherstContact):
#     contact_name: str = Field(..., alias='Delivery Contact')
#     business_name: str = Field(..., alias='Delivery Name')
#     mobile_phone: str = Field(..., alias='Delivery Telephone')
#     email_address: str = Field(..., alias='Delivery Email')

