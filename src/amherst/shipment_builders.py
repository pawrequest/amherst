from datetime import date

from amherst_core.models import AmherstCustomer, AmherstShipableBase
from pycommence.core.meta import CommenceTable
from shipaw.models.address_contact import Address, Contact, FullContact
from shipaw.models.shipment import Shipment
from shipaw.utils.consts_enums import ShipDirection


def address_from_str_and_pc(address_str, postcode, business_name) -> Address:
    addr_lines = address_str.strip().splitlines()
    town = addr_lines.pop() if len(addr_lines) > 1 else ''
    used_lines = [_ for _ in addr_lines if _]
    return Address(address_lines=used_lines, postcode=postcode, town=town, business_name=business_name)


def build_full_contact(record: AmherstShipableBase) -> FullContact:
    return FullContact(
        contact=Contact(
            name=record.delivery_contact_name,
            mobile_phone=record.delivery_contact_phone,
            email=record.delivery_contact_email,
        ),
        address=address_from_str_and_pc(
            record.delivery_address_str, record.delivery_address_pc, record.delivery_contact_business
        ),
    )



class PycommenceShipment[T: CommenceTable](Shipment):
    context: T


def build_shipment[T: CommenceTable](record: T) -> PycommenceShipment[T]:
    if isinstance(record, AmherstCustomer):
        return PycommenceShipment(
            shipping_date=date.today(),
            recipient=build_full_contact(record),
            reference=record.name,
            context=record,
            direction=ShipDirection.OUTBOUND,
        )
    else:
        raise ValueError('Unsupported record type for shipment building')
