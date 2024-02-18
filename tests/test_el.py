import os

import pytest
from dotenv import load_dotenv

from expresslinkpython.configuration import Environment
from expresslinkpython.expresslinkpython_client import ExpresslinkpythonClient
from expresslinkpython.models.authentication import Authentication
from expresslinkpython.models.base_request import FindRequest
from expresslinkpython.models.paf import PAF

ENV_FILE = r'../.env'
load_dotenv(ENV_FILE)


@pytest.fixture
def pf_auth():
    username = os.getenv('PF_EXPR_SAND_USR')
    password = os.getenv('PF_EXPR_SAND_PWD')
    auth = Authentication(username, password)
    return auth


def testmth(pf_auth):
    client = ExpresslinkpythonClient(
        environment=Environment.SANDBOX
    )
    sb = client.ship_service_soap_binding

    paf = PAF(postcode="NW6 4TE")
    find_request = FindRequest(
        authentication=pf_auth,
        paf=paf
    )

    result = sb.find(find_request)
    print(result)
    assert client is not None
