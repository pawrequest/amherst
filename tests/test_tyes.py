import pytest

from shipaw.models.pf_msg import Alert


@pytest.fixture
def alert():
    alert = Alert(message='sdgfo')
    alert = alert.model_validate(alert)
    assert alert
    return alert


def test_alerts(alerts, test_session):
    test_session.add(alerts)
    test_session.commit()
    test_session.refresh(alerts)
    assert alerts.id


def test_initial_booking_state(booking_fxt):
    assert booking_fxt
    assert booking_fxt.record
    assert booking_fxt.shipment_request
    assert booking_fxt.alerts
    assert booking_fxt.alerts.alert[0].message == 'Created'
