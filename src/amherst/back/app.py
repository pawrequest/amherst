import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastui import prebuilt_html
from fastui.dev import dev_fastapi_app
from fastapi.responses import HTMLResponse, PlainTextResponse
from loguru import logger
from sqlmodel import SQLModel, Session

from pycommence import get_csr
from .database import create_db, ENGINE
from .routers.hire_rout import router as hire_router
from ..models.hire import HireTable, INITIAL_FILTER_ARRAY, Hire

load_dotenv()


def populate_db_from_cmc(session: Session, model: type[SQLModel], db_model: type[SQLModel]):
    csr = get_csr(model.cmc_class.table_name)
    filters = model.initial_filter_array
    data = csr.set_filters(filters, get_all=True)
    cmc_raws = [model.cmc_class(**_) for _ in data]
    model_data = [model.from_cmc(_) for _ in cmc_raws]
    db_model_data = [db_model.model_validate(_) for _ in model_data]
    session.add_all(db_model_data)
    session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_db()
        with Session(ENGINE) as session:
            populate_db_from_cmc(session, Hire, HireTable)

        logger.info("tables created")
        # main_task = asyncio.create_task()
        yield

    finally:
        ...
        # main_task.cancel()
        # await asyncio.gather(main_task)


frontend_reload = "--reload" in sys.argv
if frontend_reload:
    app = dev_fastapi_app(lifespan=lifespan)
else:
    app = FastAPI(lifespan=lifespan)

app.include_router(hire_router, prefix="/api/hires")


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt() -> str:
    return "User-agent: *\nAllow: /"


@app.get("/favicon.ico", status_code=404, response_class=PlainTextResponse)
async def favicon_ico() -> str:
    return "page not found"


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="Amherst"))
