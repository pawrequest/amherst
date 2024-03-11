import argparse

import sqlmodel
from flaskwebgui import FlaskUI
import pycommence

from amherst import am_db, app_file, rec_importer, shipper
from amherst.models import hire_model


# warn = "%USERPROFILE%\.rye\shims removed from path"
def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=str)
    arg_parser.add_argument('record_name', type=str)
    return arg_parser.parse_args()


def main(category: str, record_name: str):
    with pycommence.api.csr_context(category) as csr:
        record = csr.get_record_by_name(record_name)

    pf_shipper = shipper.AmShipper.from_env(scope='SAND')
    # from amherst.models.manager2 import HireManagerDB

    am_db.create_db()

    with sqlmodel.Session(am_db.ENGINE) as session:
        if category.lower() == 'hire':
            managers = rec_importer.generic_records_to_managers(
                record,
                record_type=hire_model.Hire,
                pfcom=pf_shipper
            )
            # managers = rec_importer.hire_records_to_managers(record, pfcom=pf_shipper)
        elif category.lower() == 'sale':
            managers = rec_importer.sale_records_to_managers(record, pfcom=pf_shipper)
        # managers = rec_importer.hire_records_to_managers(record, pfcom=pf_shipper)
        else:
            raise ValueError(f'category {category} not found')
        session.add_all(managers)
        session.commit()

    fui = FlaskUI(app=app_file.app, server='fastapi')
    fui.run()


if __name__ == '__main__':
    args = parse_arguments()
    main(args.category, args.record_name)
