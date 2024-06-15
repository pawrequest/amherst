import pytest

from .conftest import Alert, AlertsDB


@pytest.fixture
def alert():
    alert = Alert(message='sdgfo')
    alert = alert.model_validate(alert)
    assert alert
    return alert


@pytest.fixture
def alerts(alert):
    alerts = AlertsDB(alert=[alert])
    alerts = alerts.model_validate(alerts)
    assert alerts
    return alerts


def test_alerts(alerts, test_session):
    test_session.add(alerts)
    test_session.commit()
    test_session.refresh(alerts)
    assert alerts.id
