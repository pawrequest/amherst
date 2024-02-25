import datetime
import os
import random

from dotenv import load_dotenv
import pytest
from sqlmodel import SQLModel, Session, create_engine

from amherst.models.hire_db import HireDB
from amherst.models.hire_in import HireIn
from amherst.models.hire_raw import HireRaw
from shipr.express import shared, types as el
from amherst.shipping.pfcom import AmShipper
from shipr import ZeepConfig
from shipr.express.enums import DeliveryTypeEnum, DepartmentEnum, ServiceCode
from shipr.express.shipment import RequestedShipmentMinimum
from pycommence import get_csr
from amherst.models import Sale
from sample_data import hire_records

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)
CONTRACT_NO = os.environ.get('PF_CONT_NUM_1')
...

SALE_NAME_OFFICE = 'Test - 18/08/2023 ref 450'
SALE_NAME_HM = 'Sexy Fish Restaurant - 23/11/2023 ref 420'
HIRE_NAME_OFFICE = 'Test - 16/08/2023 ref 31619'
HIRE_NAME_HOME = 'Test Customer - 2/21/2024 ref 43383'
DB_FILE = 'test.db'


@pytest.fixture(scope="session")
def test_session():
    engine = create_engine(f"sqlite:///{DB_FILE}")
    # engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def random_hire_record():
    rec = random.choice(hire_records)
    return rec


@pytest.fixture
def random_hire_raw(random_hire_record) -> HireRaw:
    return HireRaw(**random_hire_record, record=random_hire_record)


@pytest.fixture
def random_hire_in(random_hire_raw) -> HireIn:
    return HireIn.from_raw_cmc(random_hire_raw)

@pytest.fixture
def random_hire_db(random_hire_in) -> HireDB:
    return HireDB(cmc_in_model=random_hire_in)


@pytest.fixture
def random_hire_db2(random_hire_in) -> HireDB:
    return HireDB(cmc_in_model=random_hire_in)




@pytest.fixture
def hire_csr():
    return get_csr('Hire')


@pytest.fixture
def sale_csr():
    return get_csr('Sale')


@pytest.fixture
def sale_fxt():
    return Sale.from_name(SALE_NAME_HM)


@pytest.fixture
def hire_in():
    return HireIn.from_name(HIRE_NAME_HOME)


@pytest.fixture
def hire_db_from_name(test_session):
    return HireDB.from_namedb(HIRE_NAME_HOME, test_session)


#### ExpressLink
@pytest.fixture
def zconfig():
    wsdl = os.environ.get('PF_WSDL')
    binding = os.environ.get('PF_BINDING')
    ep = os.environ.get('PF_ENDPOINT_SAND')
    return ZeepConfig(
        binding=binding,
        wsdl=wsdl,
        auth=shared.Authentication.from_env(),
        endpoint=ep
    )


@pytest.fixture
def pfcom(zconfig):
    return AmShipper.from_config(zconfig)


@pytest.fixture
def service(pfcom):
    return pfcom.new_service()


@pytest.fixture
def address_r() -> el.AddressPF:
    return el.AddressPF(
        address_line1='30 Bennet Close',
        town='East Wickham',
        postcode='DA16 3HU',
    )


@pytest.fixture
def contact_r() -> el.ContactPF:
    return el.ContactPF(
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
