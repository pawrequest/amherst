import argparse
import os
import pathlib

from dotenv import load_dotenv
from flaskwebgui import FlaskUI, close_application

import pycommence
from amherst import app_file, am_db
from amherst.am_db import prep_db
from amherst.models import managers


# logger = get_loguru(profile='local', log_file='amherst.log')


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=str)
    arg_parser.add_argument('record_name', type=str)
    arg_parser.add_argument('env_loc', type=str, nargs='?', default=None)
    return arg_parser.parse_args()


def main(
        category: str = None,
        record_name: str = None,
        env_loc: str = None
):
    if not all([category, record_name, env_loc]):
        args = parse_arguments()

        category = category or args.category
        record_name = record_name or args.record_name
        env_loc = env_loc or args.env_loc or os.environ.get('AMHERST_ENV')
        env_path = pathlib.Path(env_loc)
        if not env_path.resolve().exists():
            raise FileNotFoundError(f'Environment file not found at {env_loc}')

    load_dotenv(env_loc)
    am_db.create_db()

    with pycommence.api.csr_context(category) as csr:
        record = csr.record_by_name(record_name)
        am_db.prep_db(category, record)

    try:
        fui = FlaskUI(
            fullscreen=True,
            app=app_file.app,
            server='fastapi',
            # height=1600,
            # width=1000,
            # on_shutdown=lambda: sys.exit(0)

        )
        fui.run()
    finally:
        close_application()


if __name__ == '__main__':
    args = parse_arguments()
    main(args.category, args.record_name, args.env_loc)
