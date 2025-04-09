import functools
import os
from pathlib import Path


@functools.lru_cache
def get_ampr():
    amherstpr = os.getenv('AMHERSTPR')
    if not amherstpr:
        raise ValueError('AMHERSTPR environment variable not set')
    amherstpr = Path(amherstpr)
    if not amherstpr.exists():
        raise ValueError(f'{amherstpr} directory does not exist.')
    return amherstpr


AMHERSTPR = get_ampr()


def set_env(filename: str, keyname: str):
    env_file = AMHERSTPR / filename
    if not env_file.exists():
        raise ValueError(f'{env_file} env file does not exist.')
    os.environ[keyname.upper()] = str(env_file)
    return env_file


def set_live_env():
    set_env('pf.env', 'SHIP_ENV')
    set_env('am.env', 'AM_ENV')


def set_sandbox_env():
    set_env('pf_sandbox.env', 'SHIP_ENV')
    set_env('am_sandbox.env', 'AM_ENV')


def set_amherstpr_env(sandbox: bool = False):
    if sandbox:
        set_sandbox_env()
    else:
        set_live_env()
