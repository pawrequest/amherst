"""Wrap FastAPI app in FlaskWebGUI for desktop application."""

from __future__ import annotations

import socket
import sys
import webbrowser

from flaskwebgui import FlaskUI, close_application
from jinja2.utils import url_quote
from loguru import logger

from amherst import app
from amherst.models.commence_adaptors import CategoryName


async def pycommence_shipper(category: CategoryName, record_name: str):
    url_suffix = await get_pycommence_shipper_url(category, record_name)
    await run_desktop_ui(url_suffix)


async def port_in_use(host='127.0.0.1', port=8000) -> bool:
    return socket.socket().connect_ex((host, port)) == 0


async def check_port(port=8000) -> None:
    if await port_in_use(port=port):
        raise OSError(f'Port {port} is already in use — is another instance running?')


async def run_desktop_ui(url_suffix='', port=8000):
    app.app.starting_url = url_suffix
    try:
        await check_port(port)
        await run_ui(port, url_suffix)
    except OSError as e:
        logger.error(str(e))
        sys.exit(1)
    finally:
        close_application()


async def run_ui(port: int, url_suffix: str):
    logger.info(f'Running WebFlaskUI @url={url_suffix}')
    FlaskUI(
        fullscreen=True,
        # app=app.app,
        server='fastapi',
        # port=port,
        app_mode=False,
        server_kwargs={
            'app': app.app,
            'port': port,
            'access_log': False,  # disables uvicorn access logging
            # 'log_level': 'warning',  # suppresses uvicorn's own info messages too
        },
    ).run()


async def get_pycommence_shipper_url(category: CategoryName, record_name: str) -> str:
    return (
        f'shipaw/ship_form_am?csrname={url_quote(category)}&pk_value={url_quote(record_name)}&condition=equal&max_rtn=1'
    )


REVIEW_URL = r'/shipaw/order_review_am'
CONFIRM_URL = r'/shipaw/post_confirm_am'
