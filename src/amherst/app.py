import sys
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastui import prebuilt_html
from fastui.dev import dev_fastapi_app
from fastapi.responses import HTMLResponse, PlainTextResponse
from loguru import logger
from sqlmodel import Session

from amherst import database

# from amherst.models.booking_state_db import HireState  # noqa F401
from amherst.routers import booking_router, hire_router, main_router
from amherst.front.pages.server_load import router as server_load_router

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        database.create_db()
        with Session(database.ENGINE) as session:
            database.populate_db_from_cmc(session)

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
app.include_router(server_load_router, prefix="/api/sl")
app.include_router(main_router, prefix="/api")


# app.include_router(rout, prefix="/api/rout")


@app.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt() -> str:
    return "User-agent: *\nAllow: /"


@app.get("/favicon.ico", status_code=404, response_class=PlainTextResponse)
async def favicon_ico() -> str:
    return "page not found"


@app.get("/{path:path}")
async def html_landing() -> HTMLResponse:
    return HTMLResponse(prebuilt_html(title="Amherst"))
