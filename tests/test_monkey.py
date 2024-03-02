import pydantic
from fastapi import FastAPI
from starlette.testclient import TestClient

from . import monkey

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


# class HireIn(BaseModel):
#     __tablename__ = "hire"
#     cmc_table_name: ClassVar[str] = "Hire"
#     initial_filter_array: ClassVar[FilterArray] = Field(default=INITIAL_FILTER_ARRAY2, sa_column=Column(JSON))
#     record: dict = Field(sa_column=Column(JSON))
#     state: Optional[BookingStateIn] = Field(None, sa_column=Column(JSON))


def test_address(fake_address, long_address, pfcom, test_session):
    chosen = pfcom.choose_address(fake_address)
    addr = monkey.AddressRecipient.model_validate(chosen)
    addr = addr.model_validate(addr)
    assert addr is not None
    test_session.add(addr)
    test_session.commit()
    test_session.refresh(addr)
    db_entry = test_session.get(monkey.AddressRecipientDB, addr.id)
    assert db_entry is not None


def test_contact(fake_contact, test_session):
    con = fake_contact.model_validate(fake_contact)
    assert con is not None
    # test_session.add(con)
    # test_session.commit()
    # test_session.refresh(con)
    # db_entry = test_session.get(fc.Contact, con.id)
    # assert db_entry is not None

