from datetime import date

from fastapi.testclient import TestClient

from amherst.main import app
from amherst.models import Hire

client = TestClient(app)


def test_index():
    r = client.get("/")
    assert r.status_code == 200, r.text
    assert r.text.startswith("<!doctype html>\n")
    assert r.headers.get("content-type") == "text/html; charset=utf-8"


def test_hire_router():
    response = client.get("/api/hire/id/1")
    # print(f"Status Code: {response.status_code}")
    ...


def test_hire_db_session(random_hire_db: Hire, test_session):
    random_hire_db = Hire.validate(random_hire_db)
    test_session.add(random_hire_db)
    test_session.commit()
    test_session.refresh(random_hire_db)
    assert random_hire_db.id is not None
    assert random_hire_db.ship_date >= date.today()


def test_get_hire_db(random_hire_db):
    assert isinstance(random_hire_db, Hire)


def test_contact(random_contact):
    assert random_contact.business_name
    assert random_contact.email_address
    assert random_contact.mobile_phone


def test_create_item():
    response = client.post(
        "/book/items/",
        json={
            "name": "Sample Item",
        },
    )
    assert response.status_code == 200
    assert response.json() == {
        "name": "Sample Item",
    }
