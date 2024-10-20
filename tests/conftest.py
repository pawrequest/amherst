# from dotenv import load_dotenv
import pytest
from sqlmodel import SQLModel, Session, create_engine

from shipaw import ELClient, pf_config
from shipaw.models import pf_models, pf_top

# from . import monkey as el_types

...

SALE_NAME_OFFICE = 'Test - 18/08/2023 ref 450'
SALE_NAME_HM = 'Sexy Fish Restaurant - 23/11/2023 ref 420'
HIRE_NAME_OFFICE = 'Test - 16/08/2023 ref 31619'
HIRE_NAME_HOME = 'Test Customer - 2/21/2024 ref 43383'
DB_FILE = 'sqlite:///test.db'
DB_MEMORY = 'sqlite:///:memory:'

HIRE_NAME_ENCODED = 'UG9ydHNtb3V0aCBQcmlkZSAtIDAyLzA3LzIwMjQgcmVmIDIwMzU5'


# COMMENCE


# FASTAPI
@pytest.fixture(scope='session')
def test_session():
    engine = create_engine(DB_MEMORY)
    # engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


# ExpressLink

@pytest.fixture
def sett():
    settings = pf_config.pf_sandbox_sett()
    pf_config.PFSandboxSettings.model_validate(settings, from_attributes=True)
    yield settings


@pytest.fixture
def el_client(sett):
    yield ELClient(settings=sett)


@pytest.fixture
def fake_address():
    addr = pf_models.AddressRecipient.model_validate(
        dict(
            address_line1='30 Bennet Close',
            town='East Wickham',
            postcode='DA16 3HU',
        )
    )
    return addr.model_validate(addr)


@pytest.fixture
def long_address():
    addr = pf_models.AddressRecipient.model_validate(
        dict(
            address_line1='30 Bennet Close' * 10,
            town='East Wickham',
            postcode='DA16 3HU',
        )
    )
    return addr.model_validate(addr)


@pytest.fixture
def fake_contact() -> pf_top.Contact:
    return pf_top.Contact(
        business_name='Test Business',
        email_address='notreal@fake.com',
        mobile_phone='1234567890',
    )


@pytest.fixture
def hire_record():
    return {
        'Actual Return Date': '',
        'All Address': 'Test\r\nTest\r\n12 sime affdresss\r\nME8 8SP\r\n\r\n013w3 w533',
        'Bar Codes': '',
        'Booked Date': '20240220',
        'Boxes': '1',
        'Closed': 'FALSE',
        'Cmc Table Name': 'Hire',
        'DB label printed': 'FALSE',
        'Delivery Address': '12 sime affdresss',
        'Delivery Contact': 'Test',
        'Delivery Cost': '11.00',
        'Delivery Description': '',
        'Delivery Email': 'fake@ssudfghdsfhglosdgh.com',
        'Delivery Name': 'Test',
        'Delivery Postcode': 'ME8 8SP',
        'Delivery Ref': '',
        'Delivery Tel': '013w3 w533',
        'Discount Description': '',
        'Discount Percentage': '',
        'Due Back Date': '20240305',
        'Has document Log': '',
        'Hire Sheet Printed': 'FALSE',
        'Hire Sheet Text': '\r\n* 4 x Hytera Digital radios\r\n\r\n* 1 x six-slot radio charger units\r\n\r\n* 4 x remote speaker / microphones\r\n\r\n* 4 x extra radio battery packs\r\n\r\n* 4 x vehicle power leads\r\n\r\n* 4 x repeaters',
        'Inbound ID': '',
        'Instruc Icom': 'FALSE',
        'Instruc Megaphone': 'FALSE',
        'Instruc Walkies': 'FALSE',
        'Inv Batt Desc': 'Hire of spare battery pack',
        'Inv Batt Price': '1.00',
        'Inv Batt Qty': '4',
        'Inv Bighead Desc': '',
        'Inv Bighead Price': '',
        'Inv Bighead Qty': '',
        'Inv Booked Date': 'Tue 20 February 2024',
        'Inv Case Desc': '',
        'Inv Case Price': '',
        'Inv Case Qty': '',
        'Inv Charger Desc': 'Radio chargers included in price',
        'Inv Delivery Desc': 'Delivery',
        'Inv Due Back Date': 'Tue 5 March 2024',
        'Inv EM Desc': '',
        'Inv EM Price': '',
        'Inv EM Qty': '',
        'Inv EMC Desc': '',
        'Inv EMC Price': '',
        'Inv EMC Qty': '',
        'Inv Headset Desc': '',
        'Inv Headset Price': '',
        'Inv Headset Qty': '',
        'Inv Icom Desc': '',
        'Inv Icom Price': '',
        'Inv Icom Qty': '',
        'Inv Meg Batt Desc': '',
        'Inv Mega Desc': '',
        'Inv Mega Price': '',
        'Inv Mega Qty': '',
        'Inv Parrot Desc': 'Hire of speaker / microphone',
        'Inv Parrot Price': '1.00',
        'Inv Parrot Qty': '4',
        'Inv Purchase Order': '',
        'Inv Return Desc': 'Customer to Return',
        'Inv Send Desc': 'Send Date',
        'Inv Send Out Date': 'Wed 21 February 2024',
        'Inv UHF Desc': 'Hire of Hytera Digital walkie-talkie',
        'Inv UHF Price': '12.00',
        'Inv UHF Qty': '4',
        'Inv VHF Desc': '',
        'Inv VHF Price': '',
        'Inv VHF Qty': '',
        'Inv Wand Desc': '',
        'Inv Wand Price': '',
        'Inv Wand Qty': '',
        'Invoice': '',
        'Involves Equipment': '',
        'Megaphone charger': 'FALSE',
        'Missing Kit': '',
        'Name': 'Test Customer - 2/21/2024 ref 43383',
        'Number Aerial Adapt': '0',
        'Number Batteries': '4',
        'Number Cases': '0',
        'Number Clipon Aerial': '0',
        'Number EM': '0',
        'Number EMC': '0',
        'Number Headset Big': '0',
        'Number Headset': '0',
        'Number ICOM Car Lead': '4',
        'Number ICOM PSU': '0',
        'Number Icom': '0',
        'Number Magmount': '0',
        'Number Megaphone Bat': '0',
        'Number Megaphone': '0',
        'Number Parrot': '4',
        'Number Repeater': '4',
        'Number Sgl Charger': '0',
        'Number UHF 6-way': '1',
        'Number UHF': '4',
        'Number VHF 6-way': '0',
        'Number VHF': '0',
        'Number Wand Battery': '0',
        'Number Wand Charger': '0',
        'Number Wand': '0',
        'Outbound ID': '',
        'Packed By': '',
        'Packed Date': '',
        'Packed Time': '',
        'Payment Terms': 'To be paid before hire date',
        'Pickup Arranged': 'FALSE',
        'PreShip Emailed': 'FALSE',
        'Purchase Order': '',
        'Purpose': '',
        'Radio Type': 'Hytera Digital',
        'Recurring Hire': 'FALSE',
        'Reference Number': '43383',
        'Reprogrammed': 'FALSE',
        'Return Notes': '',
        'Send / Collect': 'We send, cust return',
        'Send Method': 'Parcelforce / DB',
        'Send Out Date': '20240221',
        'Sending Status': 'Fine no problem',
        'ShipMe': 'FALSE',
        'Special Kit': '',
        'Status': 'Quote given',
        'To Customer': 'Test',
        'Unpacked Date': '',
        'Unpacked Time': '',
        'Unpacked by': '',
        'Weeks': '1',
    }
