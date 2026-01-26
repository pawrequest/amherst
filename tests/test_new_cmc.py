import datetime
from pathlib import Path

import pytest
from shipaw.fapi.responses import ShipmentResponse
from shipaw.models.address import Address, Contact, FullContact

from amherst.models.cmc_update import make_update_dict
from amherst.models.shipment import AmherstShipment


def sample2():
    return AmherstShipment(
        recipient=FullContact(
            contact=Contact(
                contact_name='Test Default Del Contact',
                email_address='admin@faaaaaaaaaaaaaaaaaak.com',
                mobile_phone='07666666666',
                phone_number='07666666666'
            ),
            address=Address(
                business_name='Test Default Del Building',
                address_lines=['30 bennet default del', '', ''],
                town='sometown',
                postcode='DA16 3HU',
                county=None,
                country='GB'
            )
        ),
        sender=None,
        boxes=1,
        shipping_date=datetime.date(2026, 1, 26),
        direction='Outbound',
        own_label=None,
        reference='Test',
        context={
            'name': 'Test',
            'tracking_numbers': 'MK3454460,MK3454535,MK3454575,MK3461085,MK3461094,000000003154420928,MK3461117,000000003154420946',
            'track_out': 'NOT IMPLEMENTED', 'track_in': 'NOT IMPLEMENTED', 'customer_name': 'Test',
            'delivery_contact_name': 'Test Default Del Contact',
            'delivery_contact_business': 'Test Default Del Building', 'delivery_contact_phone': '07666 666666',
            'delivery_contact_email': 'admin@faaaaaaaaaaaaaaaaaak.com',
            'delivery_address_str': '30 bennet default del\r\nsometown', 'delivery_address_pc': 'DA16 3HU',
            'send_date': datetime.date(2026, 1, 26), 'boxes': 1, 'delivery_method': None,
            'row_id': '17:278D:0:0', 'invoice_email': '', 'accounts_email': 'admin@faaaaaaaaaaaaaaaaaak.com',
            'hires': 'not very real is this, Test - 16/08/2023 ref 31619',
            'sales': 'Test - 04/10/2023 ref 513, Test - 18/08/2023 ref 450, Test - 11/9/2024 ref 907',
            'category': 'Customer', 'pk_key': 'Name'
        }, collect_ready=datetime.time(
            9,
            0
        ), collect_closed=datetime.time(17, 0)
    )

def amherst_shipment_sample():
    return AmherstShipment(
        recipient=FullContact(
            contact=Contact(
                contact_name='Test Default Del Contact',
                email_address='admin@faaaaaaaaaaaaaaaaaak.com',
                mobile_phone='07666666666',
                phone_number='07666666666'
            ),
            address=Address(
                business_name='Test Default Del Building',
                address_lines=['30 bennet default del', '', ''],
                town='sometown',
                postcode='DA16 3HU',
                county=None,
                country='GB'
            )
        ),
        sender=None,
        boxes=1,
        shipping_date=datetime.date(2026, 1, 26),
        direction='Outbound',
        own_label=None,
        reference='Test',
        context={
            'accounts_email': 'admin@faaaaaaaaaaaaaaaaaak.com', 'boxes': 1, 'customer_name': 'Test',
            'delivery_address_pc': 'DA16 3HU', 'delivery_address_str': '30 bennet default del\r\nsometown',
            'delivery_contact_business': 'Test Default Del Building',
            'delivery_contact_email': 'admin@faaaaaaaaaaaaaaaaaak.com',
            'delivery_contact_name': 'Test Default Del Contact',
            'delivery_contact_phone': '07666 666666', 'delivery_method': None,
            'hires': 'not very real is this, Test - 16/08/2023 ref 31619', 'invoice_email': '', 'name': 'Test',
            'row_id': '17:278D:0:0',
            'sales': 'Test - 04/10/2023 ref 513, Test - 18/08/2023 ref 450, Test - 11/9/2024 ref 907',
            'send_date': '2026-01-26', 'track_in': 'NOT IMPLEMENTED', 'track_out': 'NOT IMPLEMENTED',
            'tracking_numbers': 'MK3454460,MK3454535,MK3454575,MK3461085,MK3461094,000000003154420928,MK3461117,000000003154420946'
        },
        collect_ready=datetime.time(9, 0),
        collect_closed=datetime.time(17, 0)
    )

def resp():
    return ShipmentResponse.model_validate(
        {
            'alerts': {'alert': []}, 'data': {
            'orders': {
                'account_number': None,
                'messages': {'code': 'SUCCESS', 'description': 'SUCCESS', 'error_fields': None},
                'order': {
                    'account_number': ['AB3381', 'AB3381'], 'adult_signature': 'false', 'barcode': '01824420000405',
                    'closed_at': '17:00', 'collection': {
                        'address_line_1': '70 Kingsgate Road', 'address_line_2': None, 'city': 'London',
                        'company_name': 'AMHERST', 'contact': {
                            'email': None, 'mobile_number': None, 'person_name': 'Giles Toman',
                            'phone_number': '+442073289792'
                        }, 'country_code': 'GB', 'country_name': 'United Kingdom', 'county': None,
                        'instructions': None,
                        'postal_code': 'NW6 4TE', 'safeplace': None
                    }, 'collection_date': '26/01/2026', 'custom_reference1': None, 'custom_reference2': None,
                    'custom_reference3': None, 'delivery': {
                        'address_line_1': '30 bennet default del', 'address_line_2': None, 'city': 'sometown',
                        'company_name': 'Test Default Del Building', 'contact': {
                            'email': 'admin@faaaaaaaaaaaaaaaaaak.com', 'mobile_number': '+447666666666',
                            'person_name': 'Test Default Del Contact', 'phone_number': '+447666666666'
                        }, 'country_code': 'GB', 'country_name': 'United Kingdom', 'county': None,
                        'instructions': None,
                        'postal_code': 'DA16 3HU', 'safeplace': 'NotAllowed'
                    }, 'delivery_date': '27/01/2026', 'depots': {
                        'collecting_depot': '18', 'delivery_depot': '91', 'delivery_route': '09124',
                        'is_scottish': 'false', 'presort': None, 'request_depot': '18', 'route': 'APC',
                        'seg_code': '1',
                        'zone': 'A'
                    }, 'entry_type': 'API', 'goods_info': {
                        'charge_on_delivery': '0.00', 'fragile': False, 'goods_description': 'Radios',
                        'goods_value': '1000.00', 'increased_liability': False, 'non_conv': 'false',
                        'premium': False,
                        'premium_insurance': False, 'security': False
                    }, 'item_option': 'Weight', 'label': None,
                    'messages': {'code': 'SUCCESS', 'description': 'SUCCESS', 'error_fields': None},
                    'network_name': 'APC NETWORK', 'order_number': '000000003154735662', 'product_code': 'ND16',
                    'rates': {
                        'currency': 'GBP', 'extra_charges': '0.00', 'fuel_charge': '0.00',
                        'insurance_charge': '0.00',
                        'rate': '0.00', 'total_cost': '0.00', 'vat': '0.00'
                    }, 'ready_at': '09:00', 'reference': 'Test', 'rule_name': None, 'shipment_details': {
                        'items': {
                            'height': None, 'item_number': None, 'label': None, 'length': None, 'reference': None,
                            'tracking_number': None, 'type': None, 'value': None, 'weight': None, 'width': None
                        }, 'number_of_pieces': '1', 'total_weight': '12.00', 'volumetric_weight': '0.00'
                    }, 'way_bill': '2026012601824420000405'
                }
            }
        }, 'label_path': Path(
            'C:/prdev/amdev/logs/labels/Outbound/Shipping_Label_TO_Test_Default_Del_Building_ON_2026-01-26_5.pdf'
        ), 'shipment': {
            'boxes': 1, 'collect_closed': datetime.time(17, 0), 'collect_ready': datetime.time(9, 0), 'context': {
                'accounts_email': 'admin@faaaaaaaaaaaaaaaaaak.com', 'boxes': 1, 'customer_name': 'Test',
                'delivery_address_pc': 'DA16 3HU', 'delivery_address_str': '30 bennet default del\nsometown',
                'delivery_contact_business': 'Test Default Del Building',
                'delivery_contact_email': 'admin@faaaaaaaaaaaaaaaaaak.com',
                'delivery_contact_name': 'Test Default Del Contact', 'delivery_contact_phone': '07666 666666',
                'delivery_method': None, 'hires': 'not very real is this, Test - 16/08/2023 ref 31619',
                'invoice_email': '', 'name': 'Test', 'row_id': '17:278D:0:0',
                'sales': 'Test - 04/10/2023 ref 513, Test - 18/08/2023 ref 450, Test - 11/9/2024 ref 907',
                'send_date': '2026-01-26', 'track_in': 'NOT IMPLEMENTED', 'track_out': 'NOT IMPLEMENTED',
                'tracking_numbers': 'MK3454460,MK3454535,MK3454575,MK3461085,MK3461094,000000003154420928,MK3461117,000000003154420946'
            }, 'direction': 'Outbound', 'own_label': None, 'recipient': {
                'address': {
                    'address_lines': ['30 bennet default del', '', ''],
                    'business_name': 'Test Default Del Building',
                    'country': 'GB', 'county': None, 'postcode': 'DA16 3HU', 'town': 'sometown'
                }, 'contact': {
                    'contact_name': 'Test Default Del Contact', 'email_address': 'admin@faaaaaaaaaaaaaaaaaak.com',
                    'mobile_phone': '07666666666', 'phone_number': '07666666666'
                }
            }, 'reference': 'Test', 'sender': None, 'shipping_date': datetime.date(2026, 1, 26)
        }, 'shipment_num': '000000003154735662', 'status': 'SUCCESS', 'success': True, 'template': None,
            'tracking_link': 'https://apc.hypaship.com/app/shared/customerordersoverview/index#search_form'
        }
    )

@pytest.mark.asyncio
async def test_me():
    amship = sample2()
    ship_resp = resp()
    cmc_update = await make_update_dict(amship, ship_resp)
    ...
