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
import os

from flaskwebgui import FlaskUI, close_application
from loguru import logger
from win32com.universal import com_error

import amherst.models.am_record
import amherst.models.db_models
from pycommence import PyCommence

from amherst.am_config import am_sett
from amherst.models import am_record, db_models
from amherst import am_db, app_file


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=str)
    arg_parser.add_argument('record_name', type=str)
    return arg_parser.parse_args()


async def main(category: am_record.AmherstTableEnum, record_name: str):
    # CoInitialize()
    alert = None
    booking = None
    am_db.create_db()
    print("Template directory:", os.path.abspath(am_sett().base_dir / 'front' / 'templates'))

    try:
        with PyCommence.from_table_name_context(table_name=category) as py_cmc:
            record = py_cmc.one_record(record_name)

        record['cmc_table_name'] = category
        amrec = am_record.AmherstRecord(**record)
        amrec = amrec.model_validate(amrec)
        amrec_db = amherst.models.am_record.AmherstRecordDB(**amrec.model_dump())
        booking = db_models.BookingStateDB(
            record=amrec_db,
            shipment_request=(am_db.amherst_shipment_request(amrec))
        )

        with am_db.get_session_cm() as session:
            session.add(booking)
            session.commit()
            session.refresh(booking)
            ...

        # try:
        # except ValidationError as e:
        #     msg = f'Error validating record, using partial data'
        #     logger.warning(f'{msg} \n{e}')
        #     amrec = AmherstRecordPartial(**record)
        #     amrec.alerts = [Alert(code=None, message=msg, type='WARNING')]

        # amrec = amrec.model_validate(amrec)

        # shiprec_id = am_db.amherst_record_to_shiprec(amrec)
        # assert shiprec_id, f'Error creating ShipableRecord for {amrec.name}'
        # logger.info(f'added ShipmentRecord #{shiprec_id}')

    except com_error as e:
        alert = 'Error: Commence Server execution failed. Ensure Commence is running.'

    except Exception as e:
        alert = f'Error creating ShipableRecord: {e}'

    try:
        if alert or not booking:
            logger.exception(alert)
            alert = base64.urlsafe_b64encode(alert.encode('utf-8')).decode('utf-8')
            fui = FlaskUI(
                fullscreen=True,
                app=app_file.app,
                server='fastapi',
                url_suffix=f'fail/{alert}',
            )
        else:
            fui = FlaskUI(
                fullscreen=True,
                app=app_file.app,
                server='fastapi',
                url_suffix=f'{booking.id}',
                # url_suffix=f'ship/select/{shiprec_id}',
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
