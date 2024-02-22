import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastui import prebuilt_html
from fastui.dev import dev_fastapi_app
from fastapi.responses import HTMLResponse, PlainTextResponse
from loguru import logger
from sqlmodel import SQLModel, Session

from amherst import ENGINE, Hire, HireTable, create_db, hire_router
from amherst.script import main
from pycommence import get_csr

load_dotenv()


def populate_db_from_cmc(session: Session, model: type[SQLModel], db_model: type[SQLModel]):
    # data = hire_records
    csr = get_csr(model.cmc_class.table_name)
    filters = model.initial_filter_array
    data = csr.filter_by_array(filters, get=True)
    cmc_raws = [model.cmc_class(**_) for _ in data]
    model_data = [model.from_cmc(_) for _ in cmc_raws]
    model_data_db = [db_model.model_validate(jsonable_encoder(_)) for _ in model_data]
    session.add_all(model_data_db)
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

