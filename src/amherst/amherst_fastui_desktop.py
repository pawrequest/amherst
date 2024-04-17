"""
Wrap FastAPI app in FlaskWebGUI for desktop application.
Use `Paw Request fork <https://github.com/pawrequest/flaskwebgui>`_ for URL_SUFFIX to dynamically set loading page to the retrieved record

Environment variables:
    AM_ENV: Path to environment file defining:
        - sql database location
        - log file location
        - parcelforce labels directory
    SHIP_ENV: Path to environment file defining:
        - parcelforce account numbers
        - parcelforce contract numbers
        - parcelforce username and password
        - parcelforce wsdl
        - parcelforce endpoint
        - parcelforce binding
        - parcelforce live status

"""
import argparse

from flaskwebgui import FlaskUI, close_application
from loguru import logger

import pycommence
from amherst import am_db, app_file, am_types
import pycommence
from amherst import am_db, app_file
from pycommence import cursor

# logger = get_loguru(profile='local', log_file='amherst.log')


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=str)
    arg_parser.add_argument('record_name', type=str)
    return arg_parser.parse_args()


def main(category: am_types.AmherstTableName, record_name: str):
    am_db.create_db()

    py_cmc = pycommence.PyCommence.from_table_name(table_name=category)
    record = py_cmc.one_record(record_name)
    man_id = am_db.record_to_manager(category, record)
    logger.info(f'added booking manager #{man_id}')
    try:
        fui = FlaskUI(
            fullscreen=True,
            app=app_file.app,
            server='fastapi',
            url_suffix=f'ship/select/{man_id}'
        )
        fui.run()
    except Exception as e:
        if "got an unexpected keyword argument 'url_suffix'" in str(e):
            msg = ('URL_SUFFIX is not compatible with this version of FlaskWebGui'
                   'Install PawRequest/flaskwebgui from  @ git+https://github.com/pawrequest/flaskwebgui')
            logger.exception(msg)
            raise ValueError(msg)
    finally:
        close_application()


if __name__ == '__main__':
    args = parse_arguments()
    main(args.category, args.record_name)
