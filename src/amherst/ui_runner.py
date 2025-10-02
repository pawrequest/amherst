"""Wrap FastAPI app in FlaskWebGUI for desktop application."""

from __future__ import annotations

import asyncio
import sys

from flaskwebgui import FlaskUI, close_application
from jinja2.utils import url_quote
from loguru import logger

from amherst import app
from amherst.models.commence_adaptors import CategoryName


async def run_desktop_ui(url_suffix='', port=8000):
    try:
        logger.info(f'Running WebFlaskUI @{url_suffix}')
        FlaskUI(
            fullscreen=True,
            app=app.app,
            server='fastapi',
            url_suffix=url_suffix,
            port=port,
            app_mode=False,
        ).run()
    except Exception as e:
        if "got an unexpected keyword argument 'url_suffix'" in str(e):
            msg = (
                'URL_SUFFIX is not compatible with this version of FlaskWebGui'
                'Install PawRequest/flaskwebgui from  @ git+https://github.com/pawrequest/flaskwebgui'
            )
            logger.exception(msg)
            raise ImportError(msg)
        else:
            raise
    finally:
        close_application()


async def pycommence_shipper(category: CategoryName, record_name: str):
    url_suffix = await get_pycommence_shipper_url(category, record_name)
    await run_desktop_ui(url_suffix)


async def get_pycommence_shipper_url(category: CategoryName, record_name: str) -> str:
    return (
        f'shipaw/ship_form_am?csrname={url_quote(category)}&pk_value={url_quote(record_name)}&condition=equal&max_rtn=1'
    )


REVIEW_URL = r'/shipaw/order_review_am'
CONFIRM_URL = r'/shipaw/post_confirm_am'
