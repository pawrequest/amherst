from __future__ import annotations

from pathlib import Path
from typing import Optional, ClassVar

from pydantic import BaseModel, Field

from amherst.models.shared import DateAm, ListComma, ListNewline, DateMaybe, CmcTable


class SaleCmc(CmcTable):
    """ Direct representation of Commence Sale Category"""

    table_name: ClassVar[str] = 'Sale'

    customer: str = Field(alias='To Customer')

    # order details    
    name: str = Field(alias='Name')
    lost_equipment: bool = Field(alias='Lost Equipment')
    status: str = Field(alias='Status')

    # dates
    date_ordered: DateAm = Field(alias='Date Ordered')
    date_sent: DateMaybe = Field(alias='Date Sent', default=None)

    # payment details
    invoice_terms: str = Field(alias='Invoice Terms')
    invoice: Optional[Path] = Field(alias='Invoice')
    purchase_order_print: Optional[str] = Field(alias='Purchase Order Print')
    purchase_order: Optional[str] = Field(alias='Purchase Order')

    # items
    items_ordered: ListComma = Field(alias='Items Ordered')
    serial_numbers: ListNewline = Field(alias='Serial Numbers')
    # special_radio_prog: Optional[str] = Field(alias='Special Radio Prog')

    # staff
    # order_packed_by: Optional[str] = Field(alias='Order Packed By')
    # order_taken_by: Optional[str] = Field(alias='Order Taken By')
    order_taken_by: Optional[str] = Field(alias='Handled By Staff')

    # shipping
    delivery_method: str = Field(alias='Delivery Method')
    outbound_id: Optional[str] = Field(alias='Outbound ID')
    # parcel_tracking_nums: ListComma = Field(alias='Parcel Tracking Nums')

    # notes
    notes: str = Field(alias='Notes')
    delivery_notes: str = Field(alias='Delivery Notes')

    # delivery address
    # all_delivery_address: str = Field(alias='All Delivery Address')
    delivery_address: str = Field(alias='Delivery Address')
    delivery_contact: str = Field(alias='Delivery Contact')
    delivery_email: str = Field(alias='Delivery Email')
    delivery_name: str = Field(alias='Delivery Name')
    delivery_postcode: str = Field(alias='Delivery Postcode')
    delivery_telephone: str = Field(alias='Delivery Telephone')

    # invoice address
    invoice_address: str = Field(alias='Invoice Address')
    invoice_contact: str = Field(alias='Invoice Contact')
    invoice_email: str = Field(alias='Invoice Email')
    invoice_name: str = Field(alias='Invoice Name')
    invoice_postcode: str = Field(alias='Invoice Postcode')
    invoice_telephone: str = Field(alias='Invoice Telephone')
