from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional, ClassVar, Type

from pydantic import BaseModel

from .sale_cmc import SaleCmc
from .shared import (
    AddressAm,
)
from pycommence.models.cmc_models import (
    sub_model_from_cmc,
    CmcTableRaw,
    CmcModel,
)


class Sale(CmcModel):
    cmc_class: ClassVar[Type[CmcTableRaw]] = SaleCmc

    customer: str
    name: str
    lost_equipment: bool
    status: str
    dates: SaleDates
    payment: SalePayment
    items: SaleItems
    staff: SaleStaff
    shipping: SaleShipping
    notes: SaleNotes
    delivery_address: AddressAm
    invoice_address: AddressAm

    @classmethod
    def from_cmc(cls, cmc_obj: SaleCmc) -> Sale:
        res = cls(
            customer=cmc_obj.customer,
            name=cmc_obj.name,
            lost_equipment=cmc_obj.lost_equipment,
            status=cmc_obj.status,
            dates=sub_model_from_cmc(SaleDates, cmc_obj),
            payment=sub_model_from_cmc(SalePayment, cmc_obj),
            items=sub_model_from_cmc(SaleItems, cmc_obj),
            staff=sub_model_from_cmc(SaleStaff, cmc_obj),
            shipping=sub_model_from_cmc(SaleShipping, cmc_obj),
            notes=sub_model_from_cmc(SaleNotes, cmc_obj),
            delivery_address=sub_model_from_cmc(AddressAm, cmc_obj, prepend='delivery_'),
            invoice_address=sub_model_from_cmc(AddressAm, cmc_obj, prepend='invoice_'),
        )

        return res


class SaleDates(BaseModel):
    date_ordered: date
    date_sent: Optional[date]


class SalePayment(BaseModel):
    invoice_terms: str
    invoice: Path
    purchase_order_print: str
    purchase_order: str


class SaleItems(BaseModel):
    items_ordered: list
    serial_numbers: list


class SaleStaff(BaseModel):
    order_taken_by: str
    # order_packed_by: str
    # order_taken_by: str


class SaleShipping(BaseModel):
    delivery_method: str
    outbound_id: str
    # parcel_tracking_nums: list


class SaleNotes(BaseModel):
    notes: str
    delivery_notes: str


