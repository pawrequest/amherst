import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from fastui import prebuilt_html
from fastui.dev import dev_fastapi_app
from fastapi.responses import HTMLResponse, PlainTextResponse
from loguru import logger
from sqlalchemy import Select
from sqlmodel import Session

from amherst.sample_data import hire_records
from amherst.models import HireDB
from amherst.back.routers import booking_router, hire_router
from amherst import back as ab
load_dotenv()


def populate_db_from_cmc(session: Session, model: type[HireDB]):
    data = hire_records
    # with csr_cm(model.cmc_table_name) as csr:
    #     filters = model.initial_filter_array. default
    #     data = csr.filter_by_array(filters, get=True)

    hires = [model(record=_) for _ in data]
    hires_val = [model.validate(jsonable_encoder(_)) for _ in hires]
    existing = [_[0] for _ in session.exec(Select(model.name)).all()]
    hires_new = [_ for _ in hires_val if _.name not in existing]
    session.add_all(hires_new)
    session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        ab.create_db()
        with Session(ab.ENGINE) as session:
            populate_db_from_cmc(session, HireDB)

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

app.include_router(hire_router, prefix="/api/hire")
app.include_router(booking_router, prefix="/api/book")


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt() -> str:
    return "User-agent: *\nAllow: /"


@app.get("/favicon.ico", status_code=404, response_class=PlainTextResponse)
async def favicon_ico() -> str:
    return "page not found"


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="Amherst"))
