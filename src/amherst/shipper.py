# from __future__ import annotations
from __future__ import annotations

import os

from shipr import ELClient, models, msgs, ship_ui
from shipr.models import pf_ext, pf_lists, pf_shared, pf_top


class AmherstAddress(pf_ext.BaseAddress):
    address_line1: str = '70 Kingsgate Road'
    address_line2: str = 'Kilburn'
    address_line3: str = ''
    town: str = 'London'
    postcode: str = 'NW6 4TE'
    country: str = 'GB'


am_add_dict = dict(
    address_line1='70 Kingsgate Road',
    address_line2='Kilburn',
    address_line3='',
    town='London',
    postcode='NW6 4TE',
    country='GB',
)


class AmherstContact(pf_top.Contact):
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
    def state_to_collection_request(self, state: ship_ui.ShipState):
        ship_req = state_to_amherst_collection(state)
        req = msgs.CreateCollectionRequest(
            authentication=self.config.auth,
            requested_shipment=ship_req
        )
        return req


# def booking_state_to_shipment_complex(state: ship_ui.ShipState) -> pf_top.RequestedShipmentSimple:
#     # add = elt.AddressRecipientPF.model_validate(state.address)
#     return pf_top.RequestedShipmentSimple(
#         department_id=s_types.DepartmentNum,
#         shipment_type='DELIVERY',
#         contract_number=os.environ["PF_CONT_NUM_1"],
#         service_code=state.service,
#         shipping_date=state.ship_date,
#         recipient_contact=state.contact,
#         recipient_address=state.address,
#         total_number_of_parcels=state.boxes,
#         sender_address=AmherstPFAddress,
#         sender_contact=AmherstContact,
#
#     )


def state_to_amherst_collection(state: ship_ui.ShipState) -> models.CollectionMinimum:
    col_min = models.CollectionMinimum(
        contract_number=os.environ['PF_CONT_NUM_1'],
        service_code=pf_shared.ServiceCode.EXPRESS24,
        shipping_date=state.ship_date,
        recipient_contact=AmherstContact(),
        recipient_address=pf_ext.AddressRecipient.model_validate(am_add_dict),
        total_number_of_parcels=state.boxes,
        print_own_label=True,
        collection_info=pf_top.collection_info_from_state(state),
    )
    return col_min.model_validate(col_min)
