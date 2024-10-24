import asyncio

from flaskwebgui import FlaskUI, close_application
from loguru import logger

from amherst import app

PORT = 8000
# URL_SUFFIX = 'ship/form/'
URL_SUFFIX = 'html/multi'


async def run_desktop_ui(url_suffix=URL_SUFFIX):
    try:
        logger.info(f'Starting desktop UI with URL_SUFFIX: {url_suffix}')
        fui = FlaskUI(
            fullscreen=True,
            app=app.app,
            server='fastapi',
            url_suffix=url_suffix,
            port=PORT,
            app_mode=False,
        )
        fui.run()
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


if __name__ == '__main__':
    asyncio.run(run_desktop_ui())
