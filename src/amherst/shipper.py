# from __future__ import annotations
import os

from shipr.models import pf_ext, pf_top, types as s_types
from shipr import ELClient, ship_ui


class AmherstPFAddress(pf_ext.AddressSender):
    address_line1: str = '70 Kingsgate Road'
    address_line2: str = 'Kilburn'
    address_line3: str = ''
    town: str = 'London'
    postcode: str = 'NW6 4TE'
    country: str = 'GB'


class AmherstPFContact(pf_top.Contact):
    business_name: str = 'Amherst Radio Center'
    email_address: str = 'radios@amherst.co.uk'
    mobile_phone: str = '07979147257'
    contact_name: str = 'Giles Toman'
    telephone: str = '02073289792'


class AmShipper(ELClient):
    pass


def booking_state_to_shipment_complex(state: ship_ui.ShipState) -> pf_top.RequestedShipmentSimple:
    # add = elt.AddressRecipientPF.model_validate(state.address)
    return pf_top.RequestedShipmentSimple(
        department_id=s_types.DepartmentNum,
        shipment_type='DELIVERY',
        contract_number=os.environ["PF_CONT_NUM_1"],
        service_code=state.ship_service,
        shipping_date=state.ship_date,
        recipient_contact=state.contact,
        recipient_address=state.address,
        total_number_of_parcels=state.boxes,
        sender_address=AmherstPFAddress,
        sender_contact=AmherstPFContact,

    )
