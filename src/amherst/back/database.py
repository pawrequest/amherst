from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from pycommence import Cmc


db_url = "sqlite:///:memory:"
# db_url = "sqlite:///amherst.db"
connect_args = {"check_same_thread": False}
ENGINE = create_engine(db_url, echo=False, connect_args=connect_args)


# def engine_config():
#     return {"db_url": "sqlite:///amherst.db", "connect_args": {"check_same_thread": False}}
def engine_config():
    return {"db_url": "sqlite:///:memory:", "connect_args": {"check_same_thread": False}}


def get_session(engine=None) -> Session:
    if engine is None:
        engine = ENGINE
    with Session(engine) as session:
        yield session
    session.close()


def create_db(engine=None):
    if engine is None:
        engine = ENGINE
    SQLModel.metadata.create_all(engine)


def get_cmc() -> Cmc:
    return Cmc()
