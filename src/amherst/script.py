# import argparse
# import base64
# import webbrowser
# from loguru import logger
# import uvicorn
# from dotenv import load_dotenv
#
# load_dotenv()
#
#
# def main():
#     uvicorn.run('app:app', host="127.0.0.1", port=8000, log_level="info")
#     arg_parser = argparse.ArgumentParser()
#     arg_parser.add_argument("hire_name", type=str)
#     args = arg_parser.parse_args()
#
#     adr = get_addr(args)
#
#     webbrowser.open(adr)
#
#
# def get_addr(args):
#     hire_name_encoded = base64.urlsafe_b64encode(args.hire_name.encode()).decode()
#     adr = f"http://127.0.0.1:8000/hire/{hire_name_encoded}"
#     logger.info(f"Opening {adr}")
#     return adr
#
#
# if __name__ == "__main__":
#     main()


import argparse
import base64
import webbrowser
from loguru import logger
import uvicorn
from dotenv import load_dotenv

load_dotenv()


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("hire_name", type=str)
    return arg_parser.parse_args()


def main(hire_name=None):
    uvicorn.run('amherst.app:app', host="127.0.0.1", port=8000, log_level="info")

    if hire_name is None:
        # If no hire_name is provided, parse from command line arguments
        args = parse_arguments()
        hire_name = args.hire_name

    adr = get_addr(hire_name)
    webbrowser.open(adr)


def get_addr(hire_name):
    hire_name_encoded = base64.urlsafe_b64encode(hire_name.encode()).decode()
    adr = f"http://127.0.0.1:8000/hire/{hire_name_encoded}"
    logger.info(f"Opening {adr}")
    return adr


if __name__ == "__main__":
    args = parse_arguments()
    main(args.hire_name)
