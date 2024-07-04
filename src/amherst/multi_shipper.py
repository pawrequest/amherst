import asyncio

from comtypes import CoInitialize, CoUninitialize
from flaskwebgui import FlaskUI, close_application
from loguru import logger
from sqlmodel import SQLModel, select

from amherst import app_file
from amherst.commence_filters import initial_filter
from amherst.db import create_db, get_session_cm
from amherst.models.am_record_smpl import (
    AmherstCustomerDB,
    AmherstHireDB,
    AmherstSaleDB,
    dict_to_amtable,
)
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


async def get_order(record):
    c_name = record['To Customer']
    if not c_name:
        logger.error(f'No customer name for {record}')
        return
    return dict_to_amtable(record)


async def get_or_make_customer(customer_dict, session):
    if inb := await cust_by_name(customer_dict['Name'], session):
        return inb
    return dict_to_amtable(customer_dict)


async def cust_by_name(customer_name: str, session):
    stmt = select(AmherstCustomerDB).where(AmherstCustomerDB.name == customer_name)
    inb = session.exec(stmt).first()
    return inb


# async def get_cust(am_table, session, py_cmc):
#     stmt = select(AmherstCustomerDB).where(AmherstCustomerDB.name == am_table.customer_name)
#     inb = session.exec(stmt).first()
#     if inb:
#         am_table.customer = inb
#     else:
#         filter_array = FilterArray.from_filters(FieldFilter(column='Name', value=am_table.customer_name))
#         csr = py_cmc.get_new_cursor(csrname='Customer', filter_array=filter_array)
#         rows = list(csr.rows(with_id=True, with_category=True))
#         assert len(rows) == 1
#         customer = rows[0]
#         cust_table = dict_to_amtable(customer)
#         am_table.customer = cust_table
#         return am_table


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


async def make_or_update_amtable(model_type: type[SQLModel], am_table_in, session):
    indb = session.get(model_type, am_table_in.id)
    if indb:
        [setattr(indb, k, v) for k, v in am_table_in.model_dump().items() if k not in ('row_id', 'category')]
    else:
        indb = model_type(**am_table_in.model_dump())
    return indb


async def drop_all():
    logger.warning('Dropping all records from database.')
    with get_session_cm() as session:
        for db_model in [AmherstHireDB, AmherstSaleDB, AmherstCustomerDB]:
            session.query(db_model).delete()
            session.commit()


if __name__ == '__main__':
    asyncio.run(main())

    # main(args.category, args.record_name)


async def fresh_cmc_data():
    CoInitialize()
    with get_session_cm() as session:
        await drop_all()
        py_cmc = PyCommence()
        py_cmc.set_csr('Customer', filter_array=initial_filter('Customer'))
        for record in py_cmc.csr(csrname='Customer').rows(with_id=True, with_category=True):
            order = await get_or_make_customer(record, session)
            session.add(order)

        csrnames = ['Hire', 'Sale']
        for csrname in csrnames:
            py_cmc.set_csr(csrname, filter_array=initial_filter(csrname))
            for record in py_cmc.csr(csrname=csrname).rows(count=20, with_id=True, with_category=True):
                order = await get_order(record)
                order.customer = await cust_by_name(order.customer_name, session)
                session.add(order)
        session.commit()
    CoUninitialize()
