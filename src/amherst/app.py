# from __future__ import annotations

import contextlib
import sys

import fastapi
import sqlmodel as sqm
from dotenv import load_dotenv

import fastui
import shipr
from amherst import am_db, routers, sample_data, shipper
from amherst.models import hire_manager, hire_model
from pawsupport.logging_ps.config_loguru import get_loguru
from shipr import ShipState
from shipr.models import pf_shared

load_dotenv()

logger = get_loguru(__name__)


@contextlib.asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    try:
        am_db.create_db()
        with sqm.Session(am_db.ENGINE) as session:
            pfcom = shipper.AmShipper.from_env()
            populate_db_from_cmc(session, pfcom)

        logger.info('tables created')
        # main_task = asyncio.create_task()
        yield

    finally:
        ...
        # main_task.cancel()
        # await asyncio.gather(main_task)


frontend_reload = '--reload' in sys.argv
if frontend_reload:
    app = fastui.dev.dev_fastapi_app(lifespan=lifespan)
else:
    app = fastapi.FastAPI(lifespan=lifespan)

app.include_router(routers.hire_router, prefix='/api/hire')
# app.include_router(routers.book, prefix="/api/book")
app.include_router(routers.booking_router, prefix='/api/book')
app.include_router(routers.server_load_router, prefix='/api/sl')
app.include_router(routers.forms_router, prefix='/api/forms')
app.include_router(routers.main_router, prefix='/api')


# app.include_router(rout, prefix="/api/rout")


@app.get('/robots.txt', response_class=fastapi.responses.PlainTextResponse)
async def robots_txt() -> str:
    return 'User-agent: *\nAllow: /'


@app.get('/favicon.ico', status_code=404, response_class=fastapi.responses.PlainTextResponse)
async def favicon_ico() -> str:
    return 'page not found'


@app.get('/{path:path}')
async def html_landing() -> fastapi.responses.HTMLResponse:
    return fastapi.responses.HTMLResponse(fastui.prebuilt_html(title='Amherst'))


def initial_hire_state(
    hire: hire_model.Hire,
    pfcom: shipper.ELClient,
    ship_service: pf_shared.ServiceCode = pf_shared.ServiceCode.EXPRESS24,
) -> shipr.ShipState:
    try:
        address = pfcom.choose_address(hire.input_address)
    except ValueError as e:
        logger.error(
            f"USING BAD ADDRESS no address at postcode '{hire.input_address.postcode}' for hire {hire.name}: {e}"
        )
        address = hire.input_address

    state = ShipState(
        boxes=hire.boxes,
        ship_date=hire.ship_date,
        ship_service=ship_service,
        contact=hire.contact,
        address=address,
    )
    return state.model_validate(state)


def records_to_sesh(session: sqm.Session, pfcom: shipper.AmShipper, *records: dict[str, str]):
    for record in records:
        hire_input_ = hire_model.Hire(record=record)
        hire_input = hire_input_.model_validate(hire_input_)

        state = initial_hire_state(hire_input, pfcom)

        hire_book = hire_manager.HireManagerDB(hire=hire_input, state=state)
        hb = hire_book.model_validate(hire_book)
        session.add(hb)

    session.commit()


def populate_db_from_cmc(session: sqm.Session, pfcom):
    records = sample_data.hires
    # with cmc.csr_context(hire_model.Hire.cmc_table_name) as csr:
    #     filters = hire_model.Hire.initial_filter_array.default
    #     records = csr.filter_by_array(filters, get=True)
    records = records[:3]
    records_to_sesh(session, pfcom, *records)
