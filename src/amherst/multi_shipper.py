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

from amherst.commence_adaptors import initial_filter, HireFields
from amherst.db import create_db, get_session_cm
from amherst.config import settings
from amherst import app_file
from amherst.models.multi_check import ARecord, ARecordDB
from pycommence.pycommence_v2 import PyCommence


async def main():
    create_db()
    print('Template directory:', os.path.abspath(settings().base_dir / 'front' / 'templates'))
    category = 'Hire'
    fiter_array = initial_filter(category)
    try:
        py_cmc = PyCommence.with_csr(csrname='Hire', filter_array=fiter_array)
        with get_session_cm() as session:
            for record in py_cmc.generate_records():
                arecord = ARecord(
                    category=category,
                    data=record,
                )
                arecord_db = ARecordDB.model_validate(arecord, from_attributes=True)
                session.add(arecord_db)
        session.commit()
        # records = py_cmc.records()
        # df = prep_df(records)
        # multi = Multi(category=category, df=df)
        # multi_db = MultiDB.model_validate(multi, from_attributes=True)
        # logger.info(f'{len(df)} records found from filters = {fiter_array}')

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
