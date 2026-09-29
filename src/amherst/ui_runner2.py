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
    url_suffix = await get_url_suffix(category, record_name)
    await launch_or_connect_to_gui('127.0.0.1', 8000, url_suffix)


async def launch_or_connect_to_gui(host='127.0.0.1', port=8000, url_suffix=''):
    try:
        if await port_in_use(port):
            url = f'http://{host}:{port}/{url_suffix}'
            await connect_to_ui(url)
        else:
            await launch_gui(port, url_suffix)
    except OSError as e:
        logger.error(str(e))
        sys.exit(1)
    finally:
        close_application()


async def port_in_use(port=8000) -> bool:
    return socket.socket().connect_ex(('127.0.0.1', port)) == 0


async def check_port(port=8000) -> None:
    if await port_in_use(port):
        raise OSError(f'Port {port} is already in use — is another instance running?')


async def connect_to_ui(url):
    webbrowser.open(url)


async def launch_gui(port: int, url_suffix: str = ''):
    if url_suffix:
        app.app.starting_url = url_suffix
    FlaskUI(
        fullscreen=True,
        server='fastapi',
        app_mode=False,
        server_kwargs={
            'app': app.app,
            'port': port,
            'access_log': False,  # disables uvicorn access logging
            # 'log_level': 'warning',  # suppresses uvicorn's own info messages too
        },
    ).run()


async def get_url_suffix(category: CategoryName, record_name: str) -> str:
    return (
        f'shipaw/ship_form_am?csrname={url_quote(category)}&pk_value={url_quote(record_name)}&condition=equal&max_rtn=1'
    )
