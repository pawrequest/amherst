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

from flaskwebgui import FlaskUI, close_application
from loguru import logger

from amherst.commence_adaptors import initial_filter
from amherst.db import create_db, get_session_cm
from amherst import app_file
from amherst.models.am_record_smpl import AmherstTableDB, get_amrec_db_smpl
from pycommence.pycommence_v2 import PyCommence

CATEGORY = 'Hire'


async def main():

    create_db()
    try:
        py_cmc = PyCommence.with_csr(csrname=CATEGORY, filter_array=initial_filter(CATEGORY))
        with get_session_cm() as session:
            for record in py_cmc.generate_records_ids():
                record['category'] = CATEGORY
                am_table_in = get_amrec_db_smpl(record)
                if indb := session.get(AmherstTableDB, am_table_in.row_id):
                    [setattr(indb, k, v) for k, v in am_table_in.model_dump().items() if k not in ('row_id', 'category')]
                else:
                    indb = AmherstTableDB(**am_table_in.model_dump())
                session.add(indb)
            session.commit()

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
