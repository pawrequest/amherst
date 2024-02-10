from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session


def engine_(config=None):
    config = config or engine_config()
    db_url = config["db_url"]
    connect_args = config["connect_args"]

    return create_engine(db_url, echo=False, connect_args=connect_args)


def engine_config():
    return {"db_url": "sqlite:///amherst.db", "connect_args": {"check_same_thread": False}}


def get_session(engine=None) -> Session:
    if engine is None:
        engine = engine_()
    with Session(engine) as session:
        yield session
    session.close()


def create_db(engine=None):
    if engine is None:
        engine = engine_()
    SQLModel.metadata.create_all(engine)
