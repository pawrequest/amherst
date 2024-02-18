import os
import sys

from dotenv import load_dotenv

from expresslink_python.models.authentication import Authentication
from shipr import expresslink as pf

ENV_FILE = r'C:\Users\giles\prdev\am_dev\amherst\.env'

load_dotenv(ENV_FILE)

WSDL = os.environ.get('PF_WSDL')
USERNAME = os.getenv('PF_EXPR_SAND_USR')
PASSWORD = os.getenv('PF_EXPR_SAND_PWD')
AUTH = pf.PFAuth(USERNAME, PASSWORD)
ath = Authentication(USERNAME, PASSWORD)


def main():
    ...


if __name__ == '__main__':
    main()
    sys.exit(0)
