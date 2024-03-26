import threading
import time
import webbrowser
import argparse
import pathlib

import sqlmodel
from amherst import am_db, rec_importer, shipper
from amherst.models import hire_model, managers
import uvicorn
from dotenv import load_dotenv
from loguru import logger
# load_dotenv()
import pycommence


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=str)
    arg_parser.add_argument('record_name', type=str)
    arg_parser.add_argument('env_loc', type=str)
    return arg_parser.parse_args()


def delete_all_records(session: sqlmodel.Session, model):
    statement = sqlmodel.delete(model)
    session.execute(statement)
    session.commit()


def main(
        category: str = None,
        record_name: str = None,
        env_loc: str = None
):
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(4)
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

    with sqlmodel.Session(am_db.ENGINE) as session:
        delete_all_records(session, managers.BookingManagerDB)
        item = hire_model.ShipableItem(cmc_table_name=category, record=record)
        manager = rec_importer.generic_item_to_manager(item, pfcom=pf_shipper)
        session.add(manager)
        session.commit()

        adr = f'http://127.0.0.1:8000/{manager.id}'

        logger.info(f'Opening {adr}')
        webbrowser.open(adr)

    try:
        server_thread.join()
    except KeyboardInterrupt:
        print('Server is shutting down...')


def run_server():
    uvicorn.run('amherst.app_file_jin:app', host='127.0.0.1', port=8000, log_level='info')


# class ServerReadyHandler:
#     def __init__(self, ready_event):
#         self.ready_event = ready_event
#
#     def __call__(self, record):
#         if record["level"].name == "INFO" and "Uvicorn running on" in record["message"]:
#             self.ready_event.set()

# def run_server(ready_event):
#     config = uvicorn.Config('amherst.app:app', host="127.0.0.1", port=8000, log_level="info")
#     config.log_config["handlers"]["default"]["sink"] = ServerReadyHandler(ready_event)
#     server = uvicorn.Server(config)
#     server.run()


if __name__ == '__main__':
    main()
