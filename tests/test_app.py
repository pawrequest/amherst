import pytest
from fastapi.testclient import TestClient

from amherst.app import app
from amherst.front.hire_ui import HireUI
from amherst.models.hire_db_parts import HireDates
from amherst.models.hire_db import HireDB
from pycommence.models.cmc_sql import sub_model_from_cmc_db
from typing import Type, get_type_hints

client = TestClient(app)


def test_index():
    r = client.get('/')
    assert r.status_code == 200, r.text
    assert r.text.startswith('<!doctype html>\n')
    assert r.headers.get('content-type') == 'text/html; charset=utf-8'


@pytest.fixture
def controller(hire_in, pfcom, test_session) -> HireUI:
    return HireUI(source_model=hire_in, pfcom=pfcom)


def test_controller(controller):
    assert isinstance(controller, HireUI)


def test_controller_state(controller: HireUI, test_session):
    state = controller.state
    hire = controller.source_model
    hiredb = HireDB.model_validate(hire.model_dump())
    test_session.add(hiredb)
    test_session.commit()
    test_session.refresh(hiredb)
    ...

def test_from_raw(hire_in, test_session):
    hire2 = HireDB.from_namedb(hire_in.name, test_session)
    dates = sub_model_from_cmc_db(HireDates, hire_in, test_session)
    hire2.hire_dates = dates
    test_session.add(hire2)
    test_session.commit()
    test_session.refresh(hire2)
    assert isinstance(hire2, HireDB)
    assert hire2.hire_dates == dates


def test_from_db(hire_in, test_session):
    ...
    ...