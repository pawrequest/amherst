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
import asyncio
import base64

from flaskwebgui import FlaskUI, close_application
from loguru import logger

from pycommence import PyCommence
import amherst.models.am_record
from amherst import am_db, app_file
from amherst.models.am_record import AmherstRecord


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=str)
    arg_parser.add_argument('record_name', type=str)
    return arg_parser.parse_args()


async def main(category: amherst.models.am_record.AmherstTableName, record_name: str):
    # CoInitialize()
    alert = None
    shiprec_id = None
    am_db.create_db()

    try:
        with PyCommence.from_table_name_context(table_name=category) as py_cmc:
            record = py_cmc.one_record(record_name)

        record['cmc_table_name'] = category
        amrec = AmherstRecord(**record)
        amrec = amrec.model_validate(amrec)

        shiprec_id = am_db.amherst_record_to_shiprec(amrec)
        logger.info(f'added ShipmentRecord #{shiprec_id}')

    except Exception as e:
        alert = f'Error creating ShipableRecord: {e}'
        logger.exception(alert)
        alert = base64.urlsafe_b64encode(alert.encode('utf-8')).decode('utf-8')

    # finally:
    #     CoUninitialize()

    try:
        if alert or not shiprec_id:
            logger.warning(f'alert = {alert}')
            fui = FlaskUI(
                fullscreen=True,
                app=app_file.app,
                server='fastapi',
                url_suffix=f'shared/fail/{alert}',
            )
        else:
            fui = FlaskUI(
                fullscreen=True,
                app=app_file.app,
                server='fastapi',
                url_suffix=f'ship/select/{shiprec_id}',
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
    args = parse_arguments()
    asyncio.run(main(args.category, args.record_name))

    # main(args.category, args.record_name)
