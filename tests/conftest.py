import datetime
import os

from dotenv import load_dotenv
import pytest

from amherst.models import HireTable, HireCmc, Sale, SaleCmc, Hire
from shipr.el_combadge import PFCom, PFCom2, ZeepConfig
from shipr.models.express.address import Address, Contact
from shipr.models.express.expresslink_pydantic import Authentication
from shipr.models.express.enums import DeliveryTypeEnum, DepartmentEnum, ServiceCode
from shipr.models.express.shipment import RequestedShipmentMinimum
from pycommence import Cmc, get_csr

ENV_FILE = r'../../amherst/.env'
load_dotenv(ENV_FILE)
CONTRACT_NO = os.environ.get('PF_CONT_NUM_1')
...

SALE_NAME_OFFICE = 'Test - 18/08/2023 ref 450'
HIRE_NAME_OFFICE = 'Test - 16/08/2023 ref 31619'


@pytest.fixture
def cmc_db():
    yield Cmc()


@pytest.fixture
def new_csr(cmc_db):
    return get_csr('Hire')


def get_curs_tst(cmc_db, table_name: str):
    return cmc_db.get_cursor(table_name)


@pytest.fixture
def hire_csr(cmc_db):
    return get_curs_tst(cmc_db, 'Hire')


@pytest.fixture
def sale_csr(cmc_db):
    return get_curs_tst(cmc_db, 'Sale')


## records
@pytest.fixture
def hire_rec(hire_csr) -> dict:
    return hire_csr.get_record(HIRE_NAME_OFFICE)


@pytest.fixture
def sale_rec(sale_csr) -> dict:
    return sale_csr.get_record(SALE_NAME_OFFICE)


@pytest.fixture
def hire_cmc(hire_rec):
    return HireCmc.model_validate(hire_rec)


@pytest.fixture
def sale_cmc(sale_rec):
    return SaleCmc.model_validate(sale_rec)


@pytest.fixture
def sale_fxt(sale_cmc):
    return Sale.from_cmc(sale_cmc)


@pytest.fixture
def hire_fxt(hire_cmc):
    return Hire.from_cmc(hire_cmc)


#### ExpressLink
@pytest.fixture
def pf_auth():
    username = os.getenv('PF_EXPR_SAND_USR')
    password = os.getenv('PF_EXPR_SAND_PWD')

    auth = Authentication(user_name=username, password=password)
    return auth


@pytest.fixture
def zconfig(pf_auth):
    wsdl = os.environ.get('PF_WSDL')
    binding = os.environ.get('PF_BINDING')
    ep = os.environ.get('PF_ENDPOINT_SAND')
    return ZeepConfig(
        binding=binding,
        wsdl=wsdl,
        auth=pf_auth,
        endpoint=ep
    )


@pytest.fixture
def pf_com(zconfig):
    return PFCom.from_config(zconfig)


@pytest.fixture
def pf_com2(zconfig):
    return PFCom2.from_config(zconfig)


@pytest.fixture
def service(pf_com):
    return pf_com.new_service()


@pytest.fixture
def address_r() -> Address:
    return Address(
        address_line1='30 Bennet Close',
        town='East Wickham',
        postcode='DA16 3HU',
    )


@pytest.fixture
def contact_r() -> Contact:
    return Contact(
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

