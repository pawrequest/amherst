from amherst.models import HireDB
from amherst.models.hire_in import HireIn
from amherst.models.hire_raw import HireRaw


def test_random_hire_raw(random_hire_raw):
    assert isinstance(random_hire_raw, HireRaw)


def test_random_hire_in(random_hire_in):
    assert isinstance(random_hire_in, HireIn)


def test_get_hire_db(random_hire_db):
    assert isinstance(random_hire_db, HireDB)
    ...


def test_hire_db_in_Session(random_hire_db, test_session):
    test_session.add(random_hire_db)
    test_session.commit()
    test_session.refresh(random_hire_db)
    assert random_hire_db in test_session
    ...


def test_make_and_add(random_hire_in, test_session):
    HireDB.make_and_add(random_hire_in, test_session)
    ...