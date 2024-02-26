from amherst.models import HireDB
from amherst.models.hire_raw import HireRaw

#
# def test_random_hire_raw(random_hire_raw):
#     assert isinstance(random_hire_raw, HireRaw)


def test_get_hire_db(random_hire_db):
    assert isinstance(random_hire_db, HireDB)
    ...


def test_hire_db_session(random_hire_db: HireDB, test_session):
    random_hire_db = HireDB.validate(random_hire_db)
    test_session.add(random_hire_db)
    test_session.commit()
    test_session.refresh(random_hire_db)
    assert random_hire_db.id is not None


def test_contact(random_contact):
    assert random_contact.business_name
    assert random_contact.email_address
    assert random_contact.mobile_phone

def test_address(random_address):
    assert random_address.line1
    assert random_address.line2
    assert random_address.line3
    assert random_address.postcode
    assert random_address.town