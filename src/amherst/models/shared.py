from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel

from pycommence import FilterArray, CmcFilter
from pycommence.api import entities as ent
from pycommence.api.filters import FilterCondition

SALE_CUSTOMERS = ent.Connection(
    name='SaleCustomers',
    to_table='Customers',
    from_table='Sale',
)

HIRE_CUSTOMERS = ent.Connection(
    name='HireCustomers',
    to_table='Customers',
    from_table='Hire',
)


class ContactAm(BaseModel):
    email: str
    name: str
    telephone: str


class AddressAm(BaseModel):
    # todo separate contact
    address: str
    contact: str
    email: str
    postcode: str
    telephone: str

    @property
    def addr_lines(self) -> list[str]:
        addr_lines = self.address.splitlines()
        if len(addr_lines) < 3:
            addr_lines.extend([''] * (3 - len(addr_lines)))
        elif len(addr_lines) > 3:
            addr_lines[2] = ','.join(addr_lines[2:])
        return addr_lines


    @property
    def addr_lines_dict(self) -> dict[str, str]:
        addr_lines = self.address.splitlines()
        if len(addr_lines) < 3:
            addr_lines.extend([''] * (3 - len(addr_lines)))
        elif len(addr_lines) > 3:
            addr_lines[2] = ','.join(addr_lines[2:])
        return {
            f'address_line{num}': line
            for num, line in enumerate(addr_lines, start=1)
        }


class HireStatusEnum(StrEnum):
    BOOKED_IN = 'Booked in'
    PACKED = 'Booked in and packed'
    PARTIALLY_PACKED = 'Partially packed'
    OUT = 'Out'
    RTN_OK = 'Returned all OK'
    RTN_PROBLEMS = 'Returned with problems'
    QUOTE_GIVEN = 'Quote given'
    CANCELLED = 'Cancelled'
    EXTENDED = 'Extended'
    SOLD = 'Sold To Customer'


INITIAL_FILTER_ARRAY = FilterArray(
    CmcFilter(
        field_name='Status',
        condition=FilterCondition.EQUAL_TO,
        value=HireStatusEnum.BOOKED_IN,
    ),
    CmcFilter(
        field_name='Send Out Date',
        condition=FilterCondition.AFTER,
        value='2023-01-01',
    ),
)
