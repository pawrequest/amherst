import os
from amherst.set_env import get_ampr

SANDBOX = True


def setup_env():
    amherstpr = get_ampr()
    if SANDBOX:
        ship_env = amherstpr / 'pf_sandbox.env'
    else:
        ship_env = amherstpr / 'pf.env'
    os.environ['SHIP_ENV'] = str(ship_env)
    return ship_env


def get_expresslink():
    ship_env = setup_env()
    from shipaw.expresslink_client import ELClient
    from shipaw.pf_config import PFSettings

    return ELClient(settings=PFSettings(_env_file=ship_env))


if __name__ == '__main__':
    elc = get_expresslink()
    ship_num = ''
    label = elc.get_label()
    print('complete')
    ...

