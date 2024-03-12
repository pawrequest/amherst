import argparse

import sqlmodel as sqm
from flaskwebgui import FlaskUI
import pycommence

from amherst import am_db, app_file, rec_importer, shipper
from amherst.models.hire_model import ShipableItem
from amherst.models.managers import BookingManagerDB


# warn = "%USERPROFILE%\.rye\shims removed from path"
def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=str)
    arg_parser.add_argument('record_name', type=str)
    return arg_parser.parse_args()

def delete_all_records(session: sqm.Session, model):
    statement = sqm.delete(model)
    session.execute(statement)
    session.commit()

def main(category: str, record_name: str):
    with pycommence.api.csr_context(category) as csr:
        record = csr.get_record_by_name(record_name)

    pf_shipper = shipper.AmShipper.from_env(scope='SAND')
    # from amherst.models.manager2 import HireManagerDB

    am_db.create_db()

    with sqm.Session(am_db.ENGINE) as session:
        # if category.lower() == 'hire':
        #     item = hire_model.Hire(record=record)
        # elif category.lower() == 'sale':
        #     item = sale_model.Sale(record=record)
        # else:
        #     raise ValueError(f'category {category} not found')
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
