import json
from typing import Optional

import pytest
from fastapi.encoders import jsonable_encoder
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session, Field

from amherst.models import Hire, HireCmc, HireTable
from amherst.models.shared import model_with_sub_json


@pytest.fixture
def hire_record():
    return {
        'Name': 'BSGA - 12/03/2024 ref 20405', 'Reference Number': '42,834',
        'Booked Date': '2/8/2024',
        'Send Out Date': '3/12/2024', 'Due Back Date': '3/21/2024', 'Status': 'Booked in',
        'Actual Return Date': '', 'Purpose': 'trampoline event', 'Closed': 'FALSE',
        'Inv VHF Desc': '',
        'Delivery Address': 'C/o AAAsports\r\nShakespeare Street\r\nSunderland',
        'Number Sgl Charger': '0', 'Inv UHF Price': '12.00', 'Delivery Postcode': 'SR5 2JF',
        'Invoice': 'C:\\ProgramData\\Commence\\Commence\\8.0\\Data\\FILES\\a24679.docx',
        'Delivery Name': 'BSGA', 'Payment Terms': 'Paid by card thanks', 'Number VHF': '0',
        'Number EM': '6', 'Number VHF 6-way': '0', 'Number ICOM PSU': '0',
        'Inv UHF Desc': 'Hire of Kirisun UHF walkie-talkie', 'Inv VHF Price': '',
        'Inv EM Desc': 'Hire of earpiece/microphone', 'Number Megaphone': '0',
        'Delivery Contact': 'Andi Revell', 'Delivery Tel': '03335776787',
        'Send / Collect': 'We send and pick up', 'Send Method': 'Parcelforce/DB and we collect',
        'Hire Sheet Text': '\r\n* 6 x Kirisun UHF radios\r\n\r\n* 1 x six-slot radio charger units\r\n\r\n* 6 x Earpiece/microphones (in re-usable bags)\r\n\r\n* 6 x Semi-covert earpiece/mics (in re-usable bags)\r\n\r\n* 1 x extra radio battery packs\r\n\r\n* 1 x Laminated walkie-talkie instruction sheet',
        'Special Kit': '', 'Return Notes': '', 'Number UHF': '6', 'Number UHF 6-way': '1',
        'Number Parrot': '0', 'Number Headset': '0', 'Delivery Ref': '', 'Number Batteries': '1',
        'Number Cases': '0', 'Delivery Description': '', 'Inv EM Price': '1.00',
        'Inv Batt Desc': 'Hire of spare battery pack', 'Inv Batt Price': '1.00',
        'Inv Parrot Desc': '',
        'Inv Parrot Price': '', 'Inv Headset Desc': '', 'Inv Headset Price': '',
        'Inv Case Desc': '',
        'Inv Case Price': '', 'Inv Send Desc': 'Send Date',
        'Inv Delivery Desc': 'Delivery & Collection',
        'Inv Return Desc': 'Cust. to advise when ready for collection', 'Delivery Cost': '35.00',
        'Purchase Order': '', 'Inv EM Qty': '6', 'Inv Headset Qty': '', 'Inv Parrot Qty': '',
        'Inv Batt Qty': '1', 'Inv Case Qty': '', 'Inv UHF Qty': '6', 'Inv VHF Qty': '',
        'Discount Percentage': '25%', 'Discount Description': 'Charity Discount',
        'Instruc Walkies': 'TRUE', 'Number Megaphone Bat': '0', 'Inv Mega Qty': '',
        'Inv Mega Price': '', 'Inv Mega Desc': '',
        'Inv Charger Desc': 'Radio chargers included in price', 'Inv Meg Batt Desc': '',
        'Instruc Megaphone': 'FALSE', 'Instruc Icom': 'FALSE', 'Number Icom': '0',
        'Reprogrammed': 'FALSE', 'Inv Icom Desc': '', 'Inv Icom Qty': '', 'Inv Icom Price': '',
        'Megaphone charger': 'FALSE', 'Delivery Email': 'andi.revell@aaasports.co.uk',
        'Packed By': '',
        'Unpacked by': '', 'Number EMC': '6', 'Number Headset Big': '0',
        'Inv EMC Desc': 'Hire of semi-covert earpiece/mic', 'Inv EMC Price': '2.00',
        'Inv EMC Qty': '6',
        'Inv Bighead Desc': '', 'Inv Bighead Price': '', 'Inv Bighead Qty': '',
        'Number ICOM Car Lead': '0', 'Weeks': '1', 'Boxes': '1', 'Inv Purchase Order': '',
        'Number Magmount': '0', 'Pickup Arranged': 'FALSE', 'Number Clipon Aerial': '0',
        'Recurring Hire': 'FALSE', 'Radio Type': 'Kirisun UHF', 'Inv Wand Desc': '',
        'Inv Wand Price': '', 'Inv Wand Qty': '', 'Number Wand': '0', 'Number Repeater': '0',
        'DB label printed': 'FALSE',
        'All Address': 'Andi Revell\r\nBSGA\r\nC/o AAAsports\r\nShakespeare Street\r\nSunderland\r\nSR5 2JF\r\n\r\n03335776787\r\n\r\nandi.revell@aaasports.co.uk',
        'Bar Codes': '', 'Sending Status': 'Fine no problem',
        'Inv Booked Date': 'Thu 8 February 2024',
        'Inv Send Out Date': 'Tue 12 March 2024', 'Inv Due Back Date': 'Thu 21 March 2024',
        'Number Wand Battery': '0', 'Number Wand Charger': '0', 'Number Aerial Adapt': '0',
        'Packed Date': '', 'Packed Time': '', 'Unpacked Date': '', 'Unpacked Time': '',
        'Hire Sheet Printed': 'FALSE', 'ShipMe': 'FALSE', 'Missing Kit': '', 'Outbound ID': '',
        'PreShip Emailed': 'FALSE', 'To Customer': 'BSGA', 'Has document Log': '',
        'Involves Equipment': '', 'Inbound ID': ''
    }


def test_hire_record(hire_record, test_session):
    cmc_raw = HireCmc(**hire_record)
    model_data = Hire.from_cmc(cmc_raw)
    model_data_js = jsonable_encoder(model_data)
    model_data_db = HireTable.model_validate(model_data_js)


    # smth = model_with_sub_json(model_data_db)


    test_session.add(model_data_db)
    test_session.commit()

    ...



class SimpleTestModel(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str


def test_simple_insert_and_fetch(test_session):
    test_record = SimpleTestModel(name="Test Name")
    test_session.add(test_record)
    test_session.commit()

    fetched_record = test_session.get(SimpleTestModel, test_record.id)

    assert fetched_record is not None
    assert fetched_record.name == "Test Name"
