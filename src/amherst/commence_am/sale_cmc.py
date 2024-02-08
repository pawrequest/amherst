from __future__ import annotations

from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from amherst.commence_am.shared import DateAm, ListComma, ListNewline, DateMaybe


class SaleCmc(BaseModel):
    """ Direct representation of Commence Sale Category"""

    class Config:
        extra = 'ignore'

    # order details    
    name: str = Field(alias='Name')
    lost_equipment: bool = Field(alias='Lost Equipment')
    status: str = Field(alias='Status')

    # dates
    date_ordered: DateAm = Field(alias='Date Ordered')
    date_sent: DateMaybe = Field(alias='Date Sent', default=None)

    # payment details
    invoice_terms: str = Field(alias='Invoice Terms')
    invoice: Path = Field(alias='Invoice')
    purchase_order_print: str = Field(alias='Purchase Order Print')
    purchase_order: Optional[str] = Field(alias='Purchase Order')

    # items
    items_ordered: ListComma = Field(alias='Items Ordered')
    serial_numbers: ListNewline = Field(alias='Serial Numbers')
    special_radio_prog: str = Field(alias='Special Radio Prog')

    # staff
    order_packed_by: str = Field(alias='Order Packed By')
    order_taken_by: str = Field(alias='Order Taken By')

    # shipping
    delivery_method: str = Field(alias='Delivery Method')
    outbound_id: str = Field(alias='Outbound ID')
    parcel_tracking_nums: ListComma = Field(alias='Parcel Tracking Nums')

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
