from typing import Optional

from pydantic import BaseModel, ConfigDict
from sqlalchemy import TypeDecorator
from sqlmodel import Field, JSON, SQLModel, Column
class NestedJson(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        return value.model_dump_json() if value is not None else ''

    def process_result_value(self, value, dialect):
        return MyPydanticModel.model_validate_json(value) if value else None


class ContactPFSQL(BaseModel):
    business_name: str
    email_address: str
    mobile_phone: str
class MyPydanticModel(BaseModel):
    name: str
    age: int

def serial(self):
    return self.model_dump_json()
class MyTableModel(SQLModel, table=True):
    model_config = ConfigDict(
        json_encoders={
            MyPydanticModel: serial
        }
    )
    id: Optional[int] = Field(default=None, primary_key=True)
    data: Optional[MyPydanticModel] = Field(default=None, sa_column=Column(NestedJson))


def test_insert_my_table_model(test_session):
    pydantic_model_instance = MyPydanticModel(name="John Doe", age=30)

    table_model_instance = MyTableModel()
    # table_model_instance = MyTableModel(data=pydantic_model_instance)

    test_session.add(table_model_instance)
    test_session.commit()

    db_entry = test_session.get(MyTableModel, table_model_instance.id)
    assert db_entry is not None
    assert db_entry.data.name == "John Doe"
    assert db_entry.data.age == 30
