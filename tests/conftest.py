from loguru import logger
from sqlmodel import SQLModel, Session, create_engine
import pytest

from amherst.am_db import amherst_shipment_request
from amherst.models.am_record import AmherstRecord
from amherst.models.db_models import BookingStateDB
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressRecipient
from shipaw.models.pf_msg import Alert, Alerts
from shipaw.models.pf_top import Contact
from shipaw.pf_config import PFSandboxSettings, pf_sandbox_sett

DB_FILE = 'sqlite:///test.db'
DB_MEMORY = 'sqlite:///:memory:'


@pytest.fixture(scope='session')
def test_session():
    engine = create_engine(DB_MEMORY)
    # engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def sett():
    settings = pf_sandbox_sett()
    PFSandboxSettings.model_validate(settings, from_attributes=True)
    yield settings


@pytest.fixture
def el_client(sett):
    yield ELClient(settings=sett)


@pytest.fixture
def fake_address():
    addr = AddressRecipient.model_validate(
        dict(
            address_line1='30 Bennet Close',
            town='East Wickham',
            postcode='DA16 3HU',
        )
    )
    return addr.model_validate(addr)


@pytest.fixture
def long_address():
    addr = AddressRecipient.model_validate(
        dict(
            address_line1='30 Bennet Close' * 10,
            town='East Wickham',
            postcode='DA16 3HU',
        )
    )
    return addr.model_validate(addr)


@pytest.fixture
def fake_contact() -> Contact:
    return Contact(
        business_name='Test Business',
        email_address='notreal@fake.com',
        mobile_phone='1234567890',
    )


@pytest.fixture
def sale_fixture():
    return {
        'Name': 'Test - 22/10/2022 ref 1', 'Date Ordered': '20221022', 'Date Sent': '', 'Delivery Name': 'Test',
        'Delivery Address': 'bloggs', 'Delivery Contact': 'Blogga', 'Delivery Postcode': 'DA16 3HU',
        'Delivery Telephone': '07888 888888', 'Delivery Email': '', 'Invoice Name': 'Test', 'Invoice Address': 'bloggs',
        'Invoice Telephone': '07500 000000', 'Invoice Postcode': 'ME8 8SP', 'Invoice Email': '',
        'Invoice Contact': 'Blogga', 'Status': 'Ordered Ready To Go', 'Serial Numbers': '', 'Items Ordered': '',
        'Reference Number': '431', 'Delivery Method': 'Parcelforce',
        'Invoice': 'C:\\Users\\RYZEN\\prdev\\amherst\\README.md', 'Purchase Order': '', 'Inbound ID': '',
        'Lost Equipment': 'FALSE', 'Notes': '', 'All Delivery Address': 'Blogga\r\nTest\r\nbloggs\r\nDA16 3HU',
        'Delivery Notes': '', 'Invoice Terms': 'Due for payment please', 'Purchase Order Print': '',
        'To Customer': 'Test', 'Handled By Staff': '', 'Has Document Log': '', 'Outbound ID': '',
        'cmc_table_name': 'Sale'
    }


@pytest.fixture
def customer_record():
    return {
        'Name': 'Test', 'Contact Name': 'Test', 'Address': '12 sime affdresss', 'Telephone': '07', 'Fax': '',
        'Email': '', 'Date Added': '20230823', 'Notes': '', 'Number of hires': '2', 'Postcode': '',
        'Charity Number': '', 'Status': 'Hire Prospect', 'Student Discount?': 'FALSE', 'Date Last Contact': '20230823',
        'Card Number': '', 'Card Expiry Date': '', 'Card CVV2': '', 'Web Site': 'www.sfrsfsf.com',
        'Hire Customer': 'TRUE', 'Sales Customer': 'FALSE', 'Hire Prospect': 'FALSE', 'Sales Prospect': 'FALSE',
        'Closed prospect': 'FALSE', 'Dump': '', 'AQ Ref Number': '', 'Mobile Phone': '07',
        'All Address': 'Test\r\n\r\n12 sime affdresss', 'Supplier / Other': 'FALSE', 'Discount Percentage': '',
        'Annual Event': 'FALSE', 'Annual Event Date': '', 'Deliv Address': '12 sime affdresss',
        'Deliv Postcode': 'ME8 8SP', 'Deliv Name': 'Test', 'Deliv Contact': 'Test', 'Deliv Telephone': '07999 999999',
        'Deliv Email': '', 'Purchase Order': '', 'Backorder Flag': 'FALSE', 'Backorder Details': '',
        'Number Batteries': '0', 'Number Cases': '0', 'Number EM': '0', 'Number EMC': '0', 'Number Headset': '0',
        'Number Headset Big': '0', 'Number Icom': '0', 'Number Megaphone': '0', 'Number Parrot': '0', 'Number UHF': '0',
        'Accounts Contact': '', 'Accounts Telephone': '', 'Accounts Email': '', 'Licence Applied For?': 'FALSE',
        'Licence App Date': '', 'Licence Type': '', 'Licence Ref': '', 'Charity?': 'FALSE', 'Licence Needed': 'FALSE',
        'Main Telephone': '07888 888888', 'First Hire Date': '', 'Discount Description': '', 'First Hire Details': '',
        'Special Radio Prog': '', 'Problem Customer': 'FALSE', 'Number of contacts': '1', 'Name For Printing': '',
        'ShipMe': 'FALSE', 'More Contacts': '', 'Invoice Name': '', 'Invoice Address': '', 'Invoice Contact': '',
        'Invoice Postcode': '', 'Invoice Email': '', 'Invoice Telephone': '', 'test for vbscript': '',
        'Has Hired Hire': '2308, Test Customer - 2/21/2024 ref 43383', 'Has Log': 'stsetsetsetste',
        'Related Date Customer': '', 'Has Sent Repairs': '', 'Has Radio Trial': '', 'Has WebEmails': '',
        'Carried Out Repairs': '', 'Is A Type of Organisation': '', 'Involves Sale': 'Test - 22/10/2022 ref 1',
        'Charged for Invoice': '', 'cmc_table_name': 'Customer'
    }


@pytest.fixture
def hire_record():
    return {
        'Actual Return Date': '',
        'All Address': 'Test\r\nTest\r\n12 sime affdresss\r\nME8 8SP\r\n\r\n013w3 w533',
        'Bar Codes': '',
        'Booked Date': '20240220',
        'Boxes': '1',
        'Closed': 'FALSE',
        'cmc_table_name': 'Hire',
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


@pytest.fixture(params=["hire_record", "sale_fixture", "customer_record"])
def amrec_fxt(request, test_session) -> AmherstRecord:
    record = request.getfixturevalue(request.param)
    logger.info(f'testing {record['cmc_table_name']} record: {record["Name"]}')
    amrec = AmherstRecord(**record)
    amrec = amrec.model_validate(amrec)
    return amrec


@pytest.fixture
def booking_fxt(amrec_fxt, test_session):
    booking = BookingStateDB(
        record=amrec_fxt,
        shipment_request=(amherst_shipment_request(amrec_fxt)),
        alerts=Alerts(alert=[Alert(code=None, message='Created')])
    )
    test_session.add(booking)
    test_session.commit()
    test_session.refresh(booking)
    assert booking.id
    return booking
