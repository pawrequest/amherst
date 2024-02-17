import os
import sys

from dotenv import load_dotenv

from shipr import expresslink as pf

ENV_FILE = r'C:\Users\giles\prdev\am_dev\amherst\.env'

load_dotenv(ENV_FILE)

WSDL = os.environ.get('PF_WSDL')
USERNAME = os.getenv('PF_EXPR_SAND_USR')
PASSWORD = os.getenv('PF_EXPR_SAND_PWD')
AUTH = pf.PFAuth(USERNAME, PASSWORD)


def main():
    config = pf.PFConfig(WSDL, AUTH)
    pf_client = pf.PFExpressLink(config)
    postcode = 'NW6 4TE'

    pc_response = pf_client.addresses_from_postcode(postcode)

    print(pc_response)


if __name__ == '__main__':
    main()
    sys.exit(0)
