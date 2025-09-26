"""Set environment variables as per sandbox setting."""

from __future__ import annotations

import os
from pathlib import Path


def set_one_env_file(envs_dir: Path, filename: str, keyname: str):
    env_file = envs_dir / filename
    if not env_file.exists():
        raise ValueError(f'{env_file} does not exist.')
    os.environ[keyname.upper()] = str(env_file)
    print(f'Set {keyname.upper()} to {env_file}')
    return env_file


def set_env_files(envs_dir: Path):
    print(f'Using environment files from {envs_dir}')

    set_one_env_file(envs_dir, f'amherst.env', 'AMHERST_ENV')
    set_one_env_file(envs_dir, f'parcelforce.env', 'PARCELFORCE_ENV')
    set_one_env_file(envs_dir, f'shipaw.env', 'SHIPAW_ENV')
    set_one_env_file(envs_dir, f'apc.env', 'APC_ENV')
    set_one_env_file(envs_dir, f'royal_mail.env', 'ROYAL_MAIL_ENV')
