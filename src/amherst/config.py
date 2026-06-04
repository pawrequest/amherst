from __future__ import annotations

import os
from functools import cache
from importlib.resources import files
from pathlib import Path

import pydantic as _p
from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.templating import Jinja2Templates

DEFAULT_UI_DIR: Path = Path(str(files('amherst').joinpath('ui')))
DEFAULT_AMHERST_DATA_DIR = Path.home() / 'amherst_shipper'
AMHERST_ENV_KEY = 'AMHERST_ENV'


def load_env(env_key: str) -> Path:
    amherst_env_file = Path(os.environ.get(env_key, ''))
    if not amherst_env_file or not amherst_env_file.exists():
        raise ValueError('AMHERST_ENV not set or does not exist')
    return amherst_env_file


class AmherstSettings(BaseSettings):
    log_level: str = 'DEBUG'
    data_dir: Path = DEFAULT_AMHERST_DATA_DIR
    ui_dir: Path = DEFAULT_UI_DIR

    model_config = SettingsConfigDict(frozen=True)

    @property
    def template_dir(self) -> Path:
        return self.ui_dir / 'templates'

    @computed_field
    @property
    def log_file(self) -> Path:
        return self.data_dir / 'logs' / 'amherst.log'

    @computed_field
    @property
    def ndjson_file(self) -> Path:
        return self.data_dir / 'logs' / 'amherst.ndjson'

    @property
    @cache
    def templates(self):
        return Jinja2Templates(directory=str(self.template_dir))

    @_p.model_validator(mode='after')
    def create_log_files(self):
        (self.data_dir / 'logs/').mkdir(parents=True, exist_ok=True)
        for v in (self.log_file, self.ndjson_file):
            if not v.exists():
                v.touch()
        return self

    @classmethod
    @cache
    def from_env(cls) -> AmherstSettings:
        env_path = load_env(AMHERST_ENV_KEY)
        if env_path.exists():
            setts = cls(_env_file=env_path)  # pycharm_pydantic false positive
            print(f'Loaded Amherst AmherstSettings from {env_path}')
        else:
            setts = cls()
            print(f'No env file found for AmherstSettings at {env_path}, using defaults')
        return setts


# @cache
# def amherst_settings() -> AmherstSettings:
#     am_env_file = load_env()
#     am_sets = AmherstSettings(_env_file=am_env_file)
#     configure_loguru(log_file=am_sets.log_file, level=am_sets.log_level)
#     return am_sets


AMHERST_SETTINGS = AmherstSettings.from_env()
