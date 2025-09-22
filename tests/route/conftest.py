import pytest
from fastapi.testclient import TestClient

from amherst.app import app


@pytest.fixture(scope='session')
def test_client():
    with TestClient(app) as client:
        yield client


__all__ = ['test_client']
