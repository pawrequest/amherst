from fastapi.testclient import TestClient
import pytest

from amherst.app_file import app

client = TestClient(app)


def test_book():
    response = client.post("/book/post/", json={"state": "your_ship_state"})
    print(f"Status Code: {response.status_code}")
    print(f"Headers: {response.headers}")
    print(f"Body: {response.json()}")


