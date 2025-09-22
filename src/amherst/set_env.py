"""Set environment variables as per sandbox setting."""

import functools
import os
from pathlib import Path

from loguru import logger


@functools.lru_cache
def get_envs_dir():
    envs_dir = os.getenv('AMHERSTPR')
    if not envs_dir:
        raise ValueError('AMHERSTPR environment variable not set')
    envs_dir = Path(envs_dir)
    if not envs_dir.exists():
        raise ValueError(f'{envs_dir} directory does not exist.')
    return envs_dir


def set_one_env(filename: str, keyname: str):
    env_file = get_envs_dir() / filename
    if not env_file.exists():
        raise ValueError(f'{env_file} does not exist.')
    os.environ[keyname.upper()] = str(env_file)
    logger.debug(f'Set {keyname.upper()} to {env_file}')
    return env_file


def set_amherstpr_env(sandbox: bool = False):
    envtype = 'sandbox' if sandbox else 'live'
    logger.debug(f'Setting environment to {envtype} mode.')
    set_one_env(f'amherst_{envtype}.env', 'AMHERST_ENV')
    set_one_env(f'parcelforce_{envtype}.env', 'PARCELFORCE_ENV')
    set_one_env(f'shipaw_{envtype}.env', 'SHIPAW_ENV')
    set_one_env(f'apc_{envtype}.env', 'APC_ENV')
