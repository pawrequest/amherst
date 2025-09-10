""" Set environment variables as per sandbox setting. """
import functools
import os
from pathlib import Path


@functools.lru_cache
def get_envs_dir():
    envs_dir = os.getenv('AMHERSTPR')
    if not envs_dir:
        raise ValueError('AMHERSTPR environment variable not set')
    envs_dir = Path(envs_dir)
    if not envs_dir.exists():
        raise ValueError(f'{envs_dir} directory does not exist.')
    return envs_dir


def set_env(filename: str, keyname: str):
    env_file = get_envs_dir() / filename
    if not env_file.exists():
        raise ValueError(f'{env_file} does not exist.')
    os.environ[keyname.upper()] = str(env_file)
    return env_file


def set_amherstpr_env(sandbox: bool = False):
    if sandbox:
        set_env('pf_sandbox.env', 'SHIP_ENV')
        set_env('am_sandbox.env', 'AM_ENV')
    else:
        set_env('pf.env', 'SHIP_ENV')
        set_env('am.env', 'AM_ENV')
