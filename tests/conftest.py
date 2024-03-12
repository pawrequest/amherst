import os
import random
from pathlib import Path

from dotenv import load_dotenv
import pytest
from sqlmodel import SQLModel, Session, create_engine

import pycommence
from amherst import sample_data, shipper
from amherst.models import hire_model, am_shared

from amherst.models.am_shared import AmherstFields
from shipr.models import pf_top, pf_ext

# from . import monkey as el_types

ENV_FILE = Path(r"C:\Users\RYZEN\prdev\amdev\.env").resolve()
if not ENV_FILE.is_file():
    raise FileNotFoundError(f"File not found: {ENV_FILE}")

load_dotenv(ENV_FILE)
CONTRACT_NO = os.environ.get("PF_CONT_NUM_1")
...

SALE_NAME_OFFICE = "Test - 18/08/2023 ref 450"
SALE_NAME_HM = "Sexy Fish Restaurant - 23/11/2023 ref 420"
HIRE_NAME_OFFICE = "Test - 16/08/2023 ref 31619"
HIRE_NAME_HOME = "Test Customer - 2/21/2024 ref 43383"
DB_FILE = "sqlite:///test.db"
DB_MEMORY = "sqlite:///:memory:"

HIRE_NAME_ENCODED = "UG9ydHNtb3V0aCBQcmlkZSAtIDAyLzA3LzIwMjQgcmVmIDIwMzU5"


### COMMENCE


@pytest.fixture
def hire_csr():
    with pycommence.api.csr_context("Hire") as csr:
        yield csr


@pytest.fixture
def sale_csr():
    with pycommence.api.csr_context("Sale") as csr:
        yield csr


@pytest.fixture(scope="session")
def random_hire_record():
    rec = random.choice(sample_data.hires)
    return rec



### FASTAPI
@pytest.fixture(scope="session")
def test_session():
    engine = create_engine(DB_MEMORY)
    # engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


## ExpressLink

@pytest.fixture
def pfcom():
    return shipper.ELClient.from_env()


@pytest.fixture
def random_contact(random_hire_record) -> pf_top.Contact:
    return pf_top.Contact(
        business_name=random_hire_record.get(am_shared.AmherstFields.CUSTOMER),
        email_address=random_hire_record.get(am_shared.AmherstFields.EMAIL),
        mobile_phone=random_hire_record.get(am_shared.AmherstFields.TELEPHONE),
    )


@pytest.fixture
def random_address(random_hire_record) -> pf_ext.AddressRecipient:
    return pf_ext.AddressRecipient(
        address_line1=random_hire_record.get(AmherstFields.ADDRESS),
        town='',
        postcode=random_hire_record.get(AmherstFields.POSTCODE)
    )


@pytest.fixture
def fake_address():
    addr = pf_ext.AddressRecipient.model_validate(
        dict(
            address_line1="30 Bennet Close",
            town="East Wickham",
            postcode="DA16 3HU",
        )
    )
    return addr.model_validate(addr)


@pytest.fixture
def long_address():
    addr = pf_ext.AddressRecipient.model_validate(
        dict(
            address_line1="30 Bennet Close" * 10,
            town="East Wickham",
            postcode="DA16 3HU",
        )
    )
    return addr.model_validate(addr)


@pytest.fixture
def fake_contact() -> pf_top.Contact:
    return pf_top.Contact(
        business_name="Test Business",
        email_address="notreal@fake.com",
        mobile_phone="1234567890",
    )

# @pytest.fixture
# def min_shipment_r(fake_address, fake_contact) -> el_msg.RequestedShipmentMinimum:
#     return el_msg.RequestedShipmentMinimum(
#         department_id=el_enums.DepartmentEnum.MAIN,
#         shipment_type=el_enums.DeliveryTypeEnum.DELIVERY,
#         contract_number=CONTRACT_NO,
#         service_code=el_enums.ServiceCode.EXPRESS24,
#         shipping_date=datetime.date(2024, 2, 21),
#         recipient_contact=fake_contact,
#         recipient_address=fake_address,
#         total_number_of_parcels=1,
#     )
@pytest.fixture(scope="session")
def random_hires():
    hires = [hire_model.Hire.model_validate(
        hire_model.Hire(
            record=random.choice(sample_data.hires)
        )
    ) for _ in
        range(20)]
    return hires
