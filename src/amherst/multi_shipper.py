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
import asyncio
import os

from flaskwebgui import FlaskUI, close_application
from loguru import logger

from amherst.db import get_session_cm
from amherst.commence import (
    INITIAL_HIRE_FILTER,
)
from amherst.importer import amherst_shipment_request, amrec_to_booking, cmc_record_to_amrec
# from amherst.models.am_record import AmherstRecordDB
from amherst.models.db_models import BookingStateDB
from pycommence import PyCommence
from amherst.config import settings
from amherst.models import am_record
from amherst import db, app_file


async def main():
    # CoInitialize()
    alert = None
    booking = None
    am_db.create_db()
    print("Template directory:", os.path.abspath(settings().base_dir / 'front' / 'templates'))

    try:
        with PyCommence.from_table_name_context(table_name='Hire') as py_cmc:
            records = py_cmc.records_by_array(INITIAL_HIRE_FILTER)
        logger.info(f'{len(records)} records found from filters = {INITIAL_HIRE_FILTER}')

        bookings = []
        for record in records:
            record['category'] = 'Hire'
            amrec = await cmc_record_to_amrec(record)
            booking = await amrec_to_booking(amrec)
            bookings.append(booking)

        with get_session_cm() as session:
            session.add_all(bookings)
            session.commit()
            logger.info(f'Added {len(bookings)} bookings to database')

        fui = FlaskUI(
            fullscreen=True,
            app=app_file.app,
            server='fastapi',
            url_suffix='multi',
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
    asyncio.run(main())

    # main(args.category, args.record_name)
