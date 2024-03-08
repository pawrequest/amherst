import argparse

import sqlmodel
from flaskwebgui import FlaskUI
import pycommence
from amherst.models.hire_manager import HireManagerDB

from amherst import am_db, app_file, rec_importer, shipper


# warn = "%USERPROFILE%\.rye\shims removed from path"
def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('hire_name', type=str)
    return arg_parser.parse_args()


def main(hire_name=None):
    if hire_name is None:
        args = parse_arguments()
        hire_name = args.hire_name

    with pycommence.csr_context('Hire') as csr:
        hire_rec = csr.get_record(hire_name)

    pf_shipper = shipper.AmShipper.from_env()
    from amherst.models.hire_manager import HireManagerDB

    am_db.create_db()

    with sqlmodel.Session(am_db.ENGINE) as session:
        managers = rec_importer.records_to_managers(hire_rec, pfcom=pf_shipper)
        session.add_all(managers)
        session.commit()

    fui = FlaskUI(app=app_file.app, server='fastapi')
    fui.run()


if __name__ == '__main__':
    # hn = 'Test - 16/08/2023 ref 31619'
    # main(hn)
    args = parse_arguments()
    main(args.hire_name)
