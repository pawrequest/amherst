import argparse
import pathlib

import sqlmodel as sqm
from dotenv import load_dotenv
from flaskwebgui import FlaskUI

import pycommence
from amherst import am_db, app_file, rec_importer, shipper
from amherst.models import hire_model, managers
from suppawt.logging_ps import get_loguru

logger = get_loguru(profile='local', log_file='amherst.log')


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=str)
    arg_parser.add_argument('record_name', type=str)
    arg_parser.add_argument('env_loc', type=str)
    return arg_parser.parse_args()


def delete_all_records(session: sqm.Session, model):
    statement = sqm.delete(model)
    session.execute(statement)
    session.commit()


def main(
        category: str = None,
        record_name: str = None,
        env_loc: str = None
):
    if not all([category, record_name, env_loc]):
        args = parse_arguments()

        category = category or args.category
        record_name = record_name or args.record_name
        env_loc = env_loc or args.env_loc
        env_path = pathlib.Path(env_loc)
        if not env_path.resolve().exists():
            raise FileNotFoundError(f'Environment file not found at {env_loc}')
        logger.info(f'Command line arguments:\n {category=}\n{record_name=}\n{env_loc=}')

    load_dotenv(env_loc)

    with pycommence.api.csr_context(category) as csr:
        record = csr.record_by_name(record_name)

    pf_shipper = shipper.AmShipper.from_env()

    am_db.create_db()

    with sqm.Session(am_db.ENGINE) as session:
        delete_all_records(session, managers.BookingManagerDB)
        item = hire_model.ShipableItem(cmc_table_name=category, record=record)
        manager = rec_importer.generic_item_to_manager(item, pfcom=pf_shipper)
        session.add(manager)
        session.commit()
    try:
        fui = FlaskUI(
            app=app_file.app, server='fastapi',
            # height=1600,
            # width=1000,
            fullscreen=True
        )
        fui.run()
    finally:
        ...


if __name__ == '__main__':
    args = parse_arguments()
    main(args.category, args.record_name)
