import argparse

import sqlmodel as sqm
from flaskwebgui import FlaskUI
import pycommence
from loguru import logger
from dotenv import load_dotenv

from amherst import am_db, app_file, rec_importer, shipper
from amherst.models.hire_model import ShipableItem
from amherst.models.managers import BookingManagerDB

env_loc = r"R:\paul_r\.internal\envs\ship.env"
load_dotenv(env_loc)

# warn = "%USERPROFILE%\.rye\shims removed from path"
def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=str)
    arg_parser.add_argument('record_name', type=str)
    arg_parser.add_argument('env_loc', nargs='?', type=str)
    return arg_parser.parse_args()


def delete_all_records(session: sqm.Session, model):
    statement = sqm.delete(model)
    session.execute(statement)
    session.commit()


def main(
        category: str = None,
        record_name: str = None,
):
    if not all([category, record_name]):
        logger.info('Arguments missing, using command line arguments: ')
        args = parse_arguments()

        category = category or args.category
        record_name = record_name or args.record_name
    logger.info(f'\n{category=}\n{record_name=}')

    with pycommence.api.csr_context(category) as csr:
        record = csr.get_record_by_name(record_name)

    pf_shipper = shipper.AmShipper.from_env()

    am_db.create_db()

    with sqm.Session(am_db.ENGINE) as session:
        delete_all_records(session, BookingManagerDB)
        item = ShipableItem(cmc_table_name=category, record=record)
        manager = rec_importer.generic_item_to_manager(item, pfcom=pf_shipper)
        session.add(manager)
        session.commit()
    try:
        fui = FlaskUI(app=app_file.app, server='fastapi', on_shutdown=am_db.destroy_db)
        fui.run()
    finally:
        am_db.destroy_db()


if __name__ == '__main__':
    args = parse_arguments()
    main(args.category, args.record_name)
