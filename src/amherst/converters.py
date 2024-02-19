import os
from datetime import date

from amherst.models.hire import Hire
from shipr.models.express.address import Address, Contact
from shipr.models.express.enums import DeliveryTypeEnum, DepartmentEnum, ServiceCode
from shipr.models.express.shipment import RequestedShipmentMinimum


def amherst_hire_to_contact(hire: Hire) -> Contact:
    """Convert a Hire to a Contact for the PFCom service."""
    return Contact(**hire.contact_dict)


def amherst_hire_to_address(hire: Hire) -> Address:
    """Convert a Hire to an Address for the PFCom service."""
    return Address(**hire.address_dict)


def amherst_hire_to_pfc_shipment(hire: Hire) -> RequestedShipmentMinimum:
    """Convert a Hire to a CreateShipmentRequest for the PFCom service."""
    # ...
    ship_date = hire.dates.send_out_date
    if not ship_date or ship_date < date.today():
        ship_date = date.today()
    req = RequestedShipmentMinimum(
        department_id=DepartmentEnum.MAIN,
        shipment_type=DeliveryTypeEnum.DELIVERY,
        contract_number=os.environ['PF_CONT_NUM_1'],
        service_code=ServiceCode.EXPRESS24,
        shipping_date=ship_date,
        recipient_contact=amherst_hire_to_contact(hire),
        recipient_address=amherst_hire_to_address(hire),
        total_number_of_parcels=hire.shipping.boxes,
    )
    return req
