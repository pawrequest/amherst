import pytest_asyncio
from loguru import logger

from amherst.importer import amrec_to_booking, cmc_record_to_amrec
from amherst.models.am_record import AmherstRecord
from amherst.models.db_models import BookingStateDB
from shipaw.ship_types import WEEKDAYS_IN_RANGE

FAKE_PHONE = '07666666666'
FAKE_EMAIL = 'sdgjhbsdhjkbgfjksdbkjsdbghf@djsahfbjhdbgf.com'

contact_xmpl = {
    'business_name': 'Test',
    'contact_name': 'test contact',
    'email_address': FAKE_EMAIL,
    'mobile_phone': '07666666666',
}

address_xmpl = {'address_line1': '756', 'town': 'rainham', 'postcode': 'ME8 8SP'}

customer_record_xmpl = {
    'AQ Ref Number': '',
    'Accounts Contact': '',
    'Accounts Email': '',
    'Accounts Telephone': '',
    'Address': '12 sime affdresss',
    'All Address': 'Test\r\n\r\n12 sime affdresss',
    'Annual Event Date': '',
    'Annual Event': 'FALSE',
    'Backorder Details': '',
    'Backorder Flag': 'FALSE',
    'Card CVV2': '',
    'Card Expiry Date': '',
    'Card Number': '',
    'Carried Out Repairs': '',
    'Charged for Invoice': '',
    'Charity Number': '',
    'Charity?': 'FALSE',
    'Closed prospect': 'FALSE',
    'Contact Name': 'Test',
    'Date Added': '20230823',
    'Date Last Contact': '20230823',
    'Deliv Address': address_xmpl.get('address_line1'),
    'Deliv Contact': contact_xmpl.get('contact_name'),
    'Deliv Email': contact_xmpl.get('email_address'),
    'Deliv Name': contact_xmpl.get('business_name'),
    'Deliv Postcode': address_xmpl.get('postcode'),
    'Deliv Telephone': contact_xmpl.get('mobile_phone'),
    'Discount Description': '',
    'Discount Percentage': '',
    'Dump': '',
    'Email': 'customer_Email@saldglsgl.com',
    'Fax': '',
    'First Hire Date': '',
    'First Hire Details': '',
    'Has Hired Hire': '2308, Test Customer - 2/21/2024 ref 43383',
    'Has Log': 'stsetsetsetste',
    'Has Radio Trial': '',
    'Has Sent Repairs': '',
    'Has WebEmails': '',
    'Hire Customer': 'TRUE',
    'Hire Prospect': 'FALSE',
    'Invoice Address': '',
    'Invoice Contact': '',
    'Invoice Email': '',
    'Invoice Name': '',
    'Invoice Postcode': '',
    'Invoice Telephone': '',
    'Involves Sale': 'Test - 22/10/2022 ref 1',
    'Is A Type of Organisation': '',
    'Licence App Date': '',
    'Licence Applied For?': 'FALSE',
    'Licence Needed': 'FALSE',
    'Licence Ref': '',
    'Licence Type': '',
    'Main Telephone': '07888 888888',
    'Mobile Phone': '07',
    'More Contacts': '',
    'Name For Printing': '',
    'Name': 'Test',
    'Notes': '',
    'Number Batteries': '0',
    'Number Cases': '0',
    'Number EM': '0',
    'Number EMC': '0',
    'Number Headset Big': '0',
    'Number Headset': '0',
    'Number Icom': '0',
    'Number Megaphone': '0',
    'Number Parrot': '0',
    'Number UHF': '0',
    'Number of contacts': '1',
    'Number of hires': '2',
    'Postcode': '',
    'Problem Customer': 'FALSE',
    'Purchase Order': '',
    'Related Date Customer': '',
    'Sales Customer': 'FALSE',
    'Sales Prospect': 'FALSE',
    'ShipMe': 'FALSE',
    'Special Radio Prog': '',
    'Status': 'Hire Prospect',
    'Student Discount?': 'FALSE',
    'Supplier / Other': 'FALSE',
    'Telephone': '07',
    'Web Site': 'www.sfrsfsf.com',
    'category': 'Customer',
    'test for vbscript': '',
}

hire_record_xmpl = {
    'Actual Return Date': '',
    'All Address': 'Test\r\nTest\r\n12 sime affdresss\r\nME8 8SP\r\n\r\n013w3 w533',
    'Bar Codes': '',
    'Booked Date': '20240220',
    'Boxes': '1',
    'Closed': 'FALSE',
    'DB label printed': 'FALSE',
    'Delivery Address': address_xmpl.get('address_line1'),
    'Delivery Contact': contact_xmpl.get('contact_name'),
    'Delivery Cost': '11.00',
    'Delivery Description': '',
    'Delivery Email': FAKE_EMAIL,
    'Delivery Name': contact_xmpl.get('business_name'),
    'Delivery Postcode': address_xmpl.get('postcode'),
    'Delivery Ref': '',
    'Delivery Tel': contact_xmpl.get('mobile_phone'),
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
    'Invoice': '',
    'Involves Equipment': '',
    'Megaphone charger': 'FALSE',
    'Missing Kit': '',
    'Name': 'Test Customer - 2/21/2024 ref 43383',
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
    'Send Out Date': min(WEEKDAYS_IN_RANGE),
    'Sending Status': 'Fine no problem',
    'ShipMe': 'FALSE',
    'Special Kit': '',
    'Status': 'Quote given',
    'To Customer': 'Test',
    'Unpacked Date': '',
    'Unpacked Time': '',
    'Unpacked by': '',
    'Weeks': '1',
    'category': 'Hire',
}

sale_record_xmpl = {
    'Name': 'Test - 22/10/2022 ref 1',
    'Date Ordered': '20221022',
    'Date Sent': '',
    'Delivery Name': contact_xmpl.get('business_name'),
    'Delivery Address': address_xmpl.get('address_line1'),
    'Delivery Contact': contact_xmpl.get('contact_name'),
    'Delivery Postcode': address_xmpl.get('postcode'),
    'Delivery Telephone': contact_xmpl.get('mobile_phone'),
    'Delivery Email': contact_xmpl.get('email_address'),
    'Invoice Name': 'Test',
    'Invoice Address': 'bloggs',
    'Invoice Telephone': '07500 000000',
    'Invoice Postcode': 'ME8 8SP',
    'Invoice Email': 'flseklstgks@salgdln.com',
    'Invoice Contact': 'Blogga',
    'Status': 'Ordered Ready To Go',
    'Serial Numbers': '',
    'Items Ordered': '',
    'Reference Number': '431',
    'Delivery Method': 'Parcelforce',
    'Invoice': 'C:\\Users\\RYZEN\\prdev\\amherst\\README.md',
    'Purchase Order': '',
    'Inbound ID': '',
    'Lost Equipment': 'FALSE',
    'Notes': '',
    'All Delivery Address': 'Blogga\r\nTest\r\nbloggs\r\nDA16 3HU',
    'Delivery Notes': '',
    'Invoice Terms': 'Due for payment please',
    'Purchase Order Print': '',
    'To Customer': contact_xmpl.get('business_name'),
    'Handled By Staff': '',
    'Has Document Log': '',
    'Outbound ID': '',
    'category': 'Sale',
    'DB label printed': 'FALSE',
}


@pytest_asyncio.fixture(params=[hire_record_xmpl, sale_record_xmpl, customer_record_xmpl], scope='session')
async def amrec_mock(request) -> AmherstRecord:
    """ Implicitly tests the AmherstRecord importer"""
    record = request.param
    logger.info(f'testing {record['category']} record: {record["Name"]}')
    return await cmc_record_to_amrec(record)


@pytest_asyncio.fixture(scope='session')
async def booking_mock_fxt(amrec_mock: AmherstRecord, test_session_fxt) -> BookingStateDB:
    """ Implicitly tests the BookingState Importer"""
    return await amrec_to_booking(amrec_mock)


@pytest_asyncio.fixture(scope='session')
async def booking_mock_db(test_session_fxt, booking_mock_fxt):
    """ Implictly tests the Database Session and the BookingStateDB model"""
    test_session_fxt.add(booking_mock_fxt)
    test_session_fxt.commit()
    test_session_fxt.refresh(booking_mock_fxt)
    return booking_mock_fxt
