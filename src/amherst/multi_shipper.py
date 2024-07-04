import asyncio

from comtypes import CoInitialize, CoUninitialize
from flaskwebgui import FlaskUI, close_application
from loguru import logger
from sqlmodel import select

from amherst import app_file
from amherst.commence_adaptors import initial_filter
from amherst.db import create_db, get_session_cm
from amherst.models.am_record_smpl import (
    AmherstCustomerDB,
    AmherstHireDB,
    AmherstSaleDB,
    AmherstTableDB,
    dict_to_amtable,
)
from pycommence.filters import FieldFilter, FilterArray
from pycommence.pycommence_v2 import PyCommence

PORT = 10550


async def main():
    create_db()
    try:
        # with get_temporary_session_cm() as session:
        fui = FlaskUI(
            fullscreen=True,
            app=app_file.app,
            server='fastapi',
            url_suffix='multi',
            port=PORT,
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


async def fresh_cmc_data():
    CoInitialize()
    with (get_session_cm() as session):
        await drop_all()
        py_cmc = PyCommence()

        csrnames = ['Hire', 'Sale']
        for csrname in csrnames:
            py_cmc.set_csr(csrname, filter_array=initial_filter(csrname))
            for record in py_cmc.csr(csrname=csrname).rows(with_id=True, with_category=True):
                c_name = record['To Customer']
                if not c_name:
                    logger.error(f'No customer name for {record}')
                    continue
                am_table = dict_to_amtable(record)
                stmt = select(AmherstCustomerDB).where(AmherstCustomerDB.name == c_name)
                inb = session.exec(stmt).first()
                if inb:
                    am_table.customer = inb
                else:
                    filter_array = FilterArray.from_filters(FieldFilter(column='Name', value=c_name))
                    csr = py_cmc.get_new_cursor(csrname='Customer', filter_array=filter_array)
                    rows = list(csr.rows(with_id=True, with_category=True))
                    assert len(rows) == 1
                    customer = rows[0]
                    cust_table = dict_to_amtable(customer)
                    am_table.customer = cust_table

                session.add(am_table)
        session.commit()
    CoUninitialize()


# async def import_cmc_data1():
#     CoInitialize()
#     with get_session_cm() as session:
#         py_cmc = PyCommence()
#         # for csrname in ['Hire']:
#         for csrname in ['Hire', 'Sale', 'Customer']:
#             py_cmc.set_csr(csrname)
#             py_cmc.filter_cursor(initial_filter(csrname), csrname=csrname)
#             for record in py_cmc.generate_records_ids(csrname=csrname):
#                 record['category'] = csrname
#                 am_table = dict_to_amtable(record)
#                 # table = await make_or_update_amtable(am_table, session)
#                 table = AmherstTableDB(**am_table.model_dump())
#
#                 session.add(table)
#         session.commit()
#     CoUninitialize()


async def make_or_update_amtable(am_table_in, session):
    indb = session.get(AmherstTableDB, am_table_in.id)
    if indb:
        [setattr(indb, k, v) for k, v in am_table_in.model_dump().items() if k not in ('row_id', 'category')]
    else:
        indb = AmherstTableDB(**am_table_in.model_dump())
    return indb


async def drop_all():
    logger.warning('Dropping all records from database.')
    with get_session_cm() as session:
        for db_model in [AmherstCustomerDB, AmherstHireDB, AmherstSaleDB, AmherstTableDB]:
            session.query(db_model).delete()
            session.commit()


if __name__ == '__main__':
    asyncio.run(main())

    # main(args.category, args.record_name)
