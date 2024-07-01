import asyncio

from comtypes import CoInitialize, CoUninitialize
from flaskwebgui import FlaskUI, close_application
from loguru import logger

from amherst import app_file
from amherst.commence_adaptors import initial_filter
from amherst.db import create_db, get_session_cm
from amherst.models.am_record_smpl import AmherstTableDB, get_amrec_db_smpl
from pycommence.pycommence_v2 import PyCommence


async def main():
    create_db()
    try:
        # with get_temporary_session_cm() as session:
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


async def import_cmc_data():
    CoInitialize()
    with get_session_cm() as session:
        py_cmc = PyCommence()
        # for csrname in ['Hire']:
        for csrname in ['Hire', 'Sale', 'Customer']:
            py_cmc.set_csr(csrname)
            py_cmc.filter_cursor(initial_filter(csrname), csrname=csrname)
            for record in py_cmc.generate_records_ids(count=10, csrname=csrname):
                record['category'] = csrname
                am_table = get_amrec_db_smpl(record)
                await add_or_update_amtable(am_table, session)
        session.commit()
    CoUninitialize()


async def add_or_update_amtable(am_table_in, session):
    indb = session.get(AmherstTableDB, am_table_in.row_id)
    if indb:
        [setattr(indb, k, v) for k, v in am_table_in.model_dump().items() if k not in ('row_id', 'category')]
    else:
        indb = AmherstTableDB(**am_table_in.model_dump())
    session.add(indb)


async def drop_all():
    with get_session_cm() as session:
        session.query(AmherstTableDB).delete()
        session.commit()


if __name__ == '__main__':
    asyncio.run(main())

    # main(args.category, args.record_name)
