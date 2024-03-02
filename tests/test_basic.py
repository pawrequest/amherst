import pydantic
from fastapi import FastAPI
from starlette.testclient import TestClient

# from __future__ import annotations
# if _ty.TYPE_CHECKING:
#     pass

app = FastAPI()
client_test = TestClient(app)


class Item(pydantic.BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None


@app.post("/items/")
async def create_item(item: Item):
    return {"name": item.name, "price": item.price}


def test_create_item():
    response = client_test.post(
        "/items/", json={
            "name": "Sample Item",
            "price": 15.99
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "name": "Sample Item",
        "price": 15.99
    }
