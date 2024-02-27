import datetime
import os
import random

from dotenv import load_dotenv
import pytest
from sqlmodel import SQLModel, Session, create_engine

from amherst.models.hire_db import HireDB
from amherst.models.shared import AmherstFields
from shipr.models import pf_types as elt
from amherst.shipping.pfcom import AmShipper
from shipr.expresslink_client import ZeepConfig
from shipr.models.pf_enums import DeliveryTypeEnum, DepartmentEnum, ServiceCode
from shipr.models.pf_shipment import RequestedShipmentMinimum
from pycommence import csr_context
from amherst.sample_data import hire_records

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)
CONTRACT_NO = os.environ.get('PF_CONT_NUM_1')
...

SALE_NAME_OFFICE = 'Test - 18/08/2023 ref 450'
SALE_NAME_HM = 'Sexy Fish Restaurant - 23/11/2023 ref 420'
HIRE_NAME_OFFICE = 'Test - 16/08/2023 ref 31619'
HIRE_NAME_HOME = 'Test Customer - 2/21/2024 ref 43383'
DB_FILE = 'sqlite:///test.db'
DB_MEMORY = 'sqlite:///:memory:'


### COMMENCE

@pytest.fixture(scope='session')
def random_hire_record():
    rec = random.choice(hire_records)
    return rec


@pytest.fixture
def hire_csr():
    with csr_context('Hire') as csr:
        yield csr


@pytest.fixture
def sale_csr():
    with csr_context('Sale') as csr:
        yield csr

@pytest.fixture(scope='session')
def random_hire_record():
    rec = random.choice(hire_records)
    return rec

### SQLModel
@pytest.fixture
def random_hire_db(random_hire_record) -> HireDB:
    hire = HireDB(record=random_hire_record)
    return hire.model_validate(hire)


### FASTAPI

@pytest.fixture(scope="session")
def test_session():
    engine = create_engine(DB_MEMORY)
    # engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session




### ExpressLink
@pytest.fixture
def zconfig():
    wsdl = os.environ.get('PF_WSDL')
    binding = os.environ.get('PF_BINDING')
    ep = os.environ.get('PF_ENDPOINT_SAND')
    return ZeepConfig(
        binding=binding,
        wsdl=wsdl,
        auth=elt.Authentication.from_env(),
        endpoint=ep
    )


@pytest.fixture
def pfcom(zconfig):
    return AmShipper.from_config(zconfig)


@pytest.fixture
def service(pfcom):
    return pfcom.new_service()

@pytest.fixture
def random_contact(random_hire_record) -> elt.ContactPF:
    return elt.ContactPF(
        business_name=random_hire_record.get(AmherstFields.CUSTOMER),
        email_address=random_hire_record.get(AmherstFields.EMAIL),
        mobile_phone=random_hire_record.get(AmherstFields.TELEPHONE)
    )

# @pytest.fixture
# def random_address(random_hire_record) -> elt.AddressPF:
#     return elt.AddressPF(
#         address_line1=random_hire_record.get(AmherstFields.ADDRESS),
#         town=random_hire_record.get(AmherstFields.TOWN),
#         postcode=random_hire_record.get(AmherstFields.POSTCODE)
#     )
@pytest.fixture
def address_r() -> elt.AddressPF:
    return elt.AddressPF(
        address_line1='30 Bennet Close',
        town='East Wickham',
        postcode='DA16 3HU',
    )


@pytest.fixture
def contact_r() -> elt.ContactPF:
    return elt.ContactPF(
        business_name='Test Business',
        email_address='notreal@fake.com',
        mobile_phone='1234567890',
    )


@pytest.fixture
def min_shipment_r(address_r, contact_r) -> RequestedShipmentMinimum:
    return RequestedShipmentMinimum(
        department_id=DepartmentEnum.MAIN,
        shipment_type=DeliveryTypeEnum.DELIVERY,
        contract_number=CONTRACT_NO,
        service_code=ServiceCode.EXPRESS24,
        shipping_date=datetime.date(2024, 2, 21),
        recipient_contact=contact_r,
        recipient_address=address_r,
        total_number_of_parcels=1,
    )
