import argparse
import base64
import threading
import time
import webbrowser

import uvicorn
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

aname = r'http://127.0.0.1:8000/hire/new/UG9ydHNtb3V0aCBQcmlkZSAtIDAyLzA3LzIwMjQgcmVmIDIwMzU5'


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('hire_name', type=str)
    return arg_parser.parse_args()


def main(hire_name=None):
    if hire_name is None:
        args = parse_arguments()
        hire_name = args.hire_name

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    time.sleep(1)
    hire_name_encoded = base64.urlsafe_b64encode(hire_name.encode()).decode()

    adr = f'http://127.0.0.1:8000/hire/new/{hire_name_encoded}'

    logger.info(f'Opening {adr}')
    webbrowser.open(adr)

    try:
        server_thread.join()
    except KeyboardInterrupt:
        print('Server is shutting down...')


def run_server():
    uvicorn.run('amherst.app:app', host='127.0.0.1', port=8000, log_level='info')


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
    args = parse_arguments()
    main(args.hire_name)
