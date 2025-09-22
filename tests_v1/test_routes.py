from client import test_client  # noqa: F401

PK_SEARCH = 'amps'

CSRNAME = 'Hire'


def test_get_pyc_pk(test_client):
    response = test_client.get(f'/api/pyc_pk/{CSRNAME}/{PK_SEARCH}')
    assert response.status_code == 200, f'Expected status code 200, but got {response.status_code}'


def test_get_import_pk(test_client):
    response = test_client.get(f'/api/import_pyc_pk/{CSRNAME}/{PK_SEARCH}')
    assert response.status_code == 200, f'Expected status code 200, but got {response.status_code}'
