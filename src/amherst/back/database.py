from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlmodel import SQLModel, Session

from amherst.shipping.pfcom import AmShipper
load_dotenv()
DB_URL = "sqlite:///:memory:"
# DB_URL = "sqlite:///amherst.db"
CONNECT_ARGS = {"check_same_thread": False}
ENGINE = create_engine(DB_URL, echo=False, connect_args=CONNECT_ARGS)


def engine_config():
    return {"db_url": DB_URL, "connect_args": CONNECT_ARGS}


def get_session(engine=None) -> Session:
    if engine is None:
        engine = ENGINE
    with Session(engine) as session:
        yield session
    session.close()


def get_pfc():
    return AmShipper.from_env()


def create_db(engine=None):
    if engine is None:
        engine = ENGINE
    SQLModel.metadata.create_all(engine)
