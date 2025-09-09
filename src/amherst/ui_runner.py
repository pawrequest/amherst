from __future__ import annotations

import asyncio
import sys

from flaskwebgui import FlaskUI, close_application
from jinja2.utils import url_quote
from loguru import logger

from amherst import app
from amherst.models.commence_adaptors import CategoryName

PORT = 8000
URL_SUFFIX = ''


async def run_desktop_ui(url_suffix=''):
    try:
        logger.info(f'Running WebFlaskUI @{url_suffix}')
        FlaskUI(
            fullscreen=True,
            app=app.app,
            server='fastapi',
            url_suffix=url_suffix,
            port=PORT,
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


#
# if __name__ == '__main__':
#     asyncio.run(run_desktop_ui())


async def shipper(category: CategoryName, record_name: str):
    url_suffix = (
        f'ship/ship_form?csrname={url_quote(category)}&pk_value={url_quote(record_name)}&condition=equal&max_rtn=1'
    )
    await run_desktop_ui(url_suffix)
