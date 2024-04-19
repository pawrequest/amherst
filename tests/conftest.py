# from dotenv import load_dotenv
import pytest
from sqlmodel import SQLModel, Session, create_engine
from shipaw.models import pf_ext, pf_top

from amherst import shipper

# from . import monkey as el_types

...

SALE_NAME_OFFICE = "Test - 18/08/2023 ref 450"
SALE_NAME_HM = "Sexy Fish Restaurant - 23/11/2023 ref 420"
HIRE_NAME_OFFICE = "Test - 16/08/2023 ref 31619"
HIRE_NAME_HOME = "Test Customer - 2/21/2024 ref 43383"
DB_FILE = "sqlite:///test.db"
DB_MEMORY = "sqlite:///:memory:"

HIRE_NAME_ENCODED = "UG9ydHNtb3V0aCBQcmlkZSAtIDAyLzA3LzIwMjQgcmVmIDIwMzU5"


### COMMENCE


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
    return shipper.ELClient.from_pyd()


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
