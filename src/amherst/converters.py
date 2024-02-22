import os

import shipr.models.express.expresslink_types
from amherst.models.hire import Hire
from shipr import RequestedShipmentMinimum, expresslink_types as el


def amherst_hire_to_contact(hire: Hire) -> shipr.models.express.expresslink_types.ContactPF:
    """Convert a Hire to a Contact for the PFCom service."""
    ret = shipr.models.express.expresslink_types.ContactPF(**hire.contact_dict)
    return ret


def amherst_hire_to_address(hire: Hire) -> shipr.models.express.expresslink_types.AddressPF:
    """Convert a Hire to an Address for the PFCom service."""
    ret = shipr.models.express.expresslink_types.AddressPF(
        **hire.address_dict
    )
    return ret


def amherst_hire_to_pfc_shipment(hire: Hire) -> RequestedShipmentMinimum:
    """Convert a Hire to a CreateShipmentRequest for the PFCom service."""
    # ...
    req = el.RequestedShipmentMinimum(
        department_id=el.DepartmentEnum.MAIN,
        shipment_type=el.DeliveryTypeEnum.DELIVERY,
        contract_number=os.environ['PF_CONT_NUM_1'],
        service_code=el.ServiceCode.EXPRESS24,
        shipping_date=hire.dates.send_out_date,
        recipient_contact=amherst_hire_to_contact(hire),
        recipient_address=amherst_hire_to_address(hire),
        total_number_of_parcels=hire.shipping.boxes,
    )
    return req
