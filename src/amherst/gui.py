import argparse

import sqlmodel
from flaskwebgui import FlaskUI

import pycommence
from amherst import am_db, rec_importer, shipper, main

warn = "%USERPROFILE%\.rye\shims removed from path"
def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('hire_name', type=str)
    return arg_parser.parse_args()


def main(hire_name=None):
    if hire_name is None:
        args = parse_arguments()
        hire_name = args.hire_name

    with pycommence.csr_context('Hire') as csr:
        csr: pycommence.Csr = csr
        hire_rec = csr.get_record(hire_name)
    pfcom = shipper.AmShipper.from_env()
    am_db.create_db()

    with sqlmodel.Session(am_db.ENGINE) as session:
        assert rec_importer.records_to_managers(hire_rec, session=session, pfcom=pfcom)

    fui = FlaskUI(app=main.app, server='fastapi')
    fui.url = f'http://127.0.0.1:{fui.port}/hire/view/1'
    fui.run()


if __name__ == '__main__':
    # hn = 'Test - 16/08/2023 ref 31619'
    # main(hn)
    args = parse_arguments()
    main(args.hire_name)
