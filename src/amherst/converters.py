import os
from shipr.models import express as el
from amherst.models.hire import Hire


def amherst_hire_to_contact(hire: Hire) -> el.types.ContactPF:
    """Convert a Hire to a Contact for the PFCom service."""
    ret = el.types.ContactPF(**hire.contact_dict)
    return ret


def amherst_hire_to_address(hire: Hire) -> el.types.AddressPF:
    """Convert a Hire to an Address for the PFCom service."""
    ret = el.types.AddressPF(
        **hire.address_dict
    )
    return ret


def amherst_hire_to_pfc_shipment(hire: Hire) -> el.shipment.RequestedShipmentMinimum:
    """Convert a Hire to a CreateShipmentRequest for the PFCom service."""
    # ...
    req = el.shipment.RequestedShipmentMinimum(
        department_id=el.enums.DepartmentEnum.MAIN,
        shipment_type=el.enums.DeliveryTypeEnum.DELIVERY,
        contract_number=os.environ['PF_CONT_NUM_1'],
        service_code=el.enums.ServiceCode.EXPRESS24,
        shipping_date=hire.dates.send_out_date,
        recipient_contact=amherst_hire_to_contact(hire),
        recipient_address=amherst_hire_to_address(hire),
        total_number_of_parcels=hire.shipping.boxes,
    )
    return req
