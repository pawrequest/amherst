# from __future__ import annotations
from __future__ import annotations

import os

from shipr import ELClient, msgs, ship_ui
from shipr.models import pf_ext, pf_lists, pf_shared, pf_top


class HomeAddress(pf_ext.BaseAddress):
    address_line1: str = '70 Kingsgate Road'
    address_line2: str = 'Kilburn'
    address_line3: str = ''
    town: str = 'London'
    postcode: str = 'NW6 4TE'
    country: str = 'GB'


class HomeContact(pf_top.Contact):
    business_name: str = 'Amherst Radio Center'
    email_address: str = 'radios@amherst.co.uk'
    mobile_phone: str = '07979147257'
    contact_name: str = 'Giles Toman'
    telephone: str = '02073289792'

    notifications: pf_lists.RecipientNotifications = pf_lists.RecipientNotifications(
        notification_type=[
            pf_shared.NotificationType.DELIVERY,
            pf_shared.NotificationType.EMAIL,
        ]
    )


class AmShipper(ELClient):
    def state_to_inbound_request(self, state: ship_ui.ShipState):
        ship_req = state_to_inbound_shipment(state)
        req = msgs.CreateCollectionRequest(
            authentication=self.config.auth,
            requested_shipment=ship_req
        )
        return req

    def state_to_request(self, state: ship_ui.ShipState):
        if state.direction == 'in':
            return self.state_to_inbound_request(state)
        if state.direction == 'out':
            return self.state_to_outbound_request(state)
        raise ValueError('Invalid direction')


def state_to_inbound_shipment(state: ship_ui.ShipState) -> pf_top.CollectionMinimum:
    col_min = pf_top.CollectionSimple(
        contract_number=os.environ['PF_CONT_NUM_1'],
        service_code=pf_shared.ServiceCode.EXPRESS24,
        shipping_date=state.ship_date,
        recipient_contact=HomeContact(),
        recipient_address=pf_ext.AddressRecipient.model_validate(HomeAddress().model_dump()),
        total_number_of_parcels=state.boxes,
        print_own_label=True,
        collection_info=pf_top.collection_info_from_state(state),
        reference_number1=state.reference,
        special_instructions1=state.special_instructions,
    )
    return col_min.model_validate(col_min)
