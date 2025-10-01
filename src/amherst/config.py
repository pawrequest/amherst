from __future__ import annotations

import os
import re
from datetime import date, datetime
from functools import lru_cache
from importlib.resources import files
from pathlib import Path
from urllib.parse import quote

import pydantic as _p
from dotenv import dotenv_values, load_dotenv
from fastapi.encoders import jsonable_encoder
from pawlogger import get_loguru
from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.templating import Jinja2Templates


def sanitise_id(value):
    return re.sub(r'\W|^(?=\d)', '_', value).lower()


def make_jsonable(thing) -> dict:
    # todo remove this function and use jsonable_encoder directly in templates?!
    res = jsonable_encoder(thing)
    return res


def date_int_w_ordinal(n: int):
    """Convert an integer to its ordinal as a string, e.g. 1 -> 1st, 2 -> 2nd, etc."""
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def ordinal_dt(dt: datetime | date) -> str:
    """Convert a datetime or date to a string with an ordinal day, e.g. 'Mon 1st Jan 2020'."""
    return dt.strftime(f'%a {date_int_w_ordinal(dt.day)} %b %Y')


def load_env_index(envs_index: Path) -> None:
    load_dotenv(envs_index)
    for env in ('APC_ENV', 'PARCELFORCE_ENV', 'SHIPAW_ENV', 'AMHERST_ENV'):
        if not os.getenv(env):
            raise ValueError(f'Environment variable {env} not set in {envs_index}')
        if not Path(os.getenv(env)).exists():
            raise ValueError(f'Environment variable {env} points to non-existent file {os.getenv(env)}')
        env_values = dotenv_values(Path(os.getenv('AMHERST_ENV')))
        log_file = Path(env_values.get('LOG_FILE'))
        log_level = env_values.get('LOG_LEVEL') or 'DEBUG'
        if not log_file or not log_file.parent.exists():
            raise ValueError(f'LOG_FILE not set in {os.getenv("AMHERST_ENV")}')
        get_loguru(log_file=log_file, profile='local', level=log_level)


#
def load_env() -> Path:
    ei = Path(os.environ.get('ENV_INDEX'))
    if not ei or not ei.exists():
        raise ValueError('ENV_INDEX not set or does not exist')
    load_env_index(ei)
    print(f'Loading env index from {ei}')
    amherst_env = Path(os.getenv('AMHERST_ENV'))
    print(f'Loading Amherst Settings from {amherst_env}')
    return amherst_env


# def load_amherst_settings_env():
#     amherst_env = Path(os.getenv('AMHERST_ENV'))
#     if not amherst_env or not amherst_env.exists():
#         raise ValueError(f'AMHERST_ENV ({amherst_env}) incorrectly set')
#     print(f'Loading Amherst Settings from {amherst_env}')
#     return amherst_env


class Settings(BaseSettings):
    log_dir: Path
    ui_dir: Path = files('amherst').joinpath('ui')
    # static_dir: Path
    # template_dir: Path
    templates: Jinja2Templates | None = None
    log_level: str = 'DEBUG'

    @property
    def template_dir(self) -> Path:
        return self.ui_dir / 'templates'

    @property
    def static_dir(self) -> Path:
        return self.ui_dir / 'static'

    @computed_field
    @property
    def log_file(self) -> Path:
        return self.log_dir / 'amherst.log'

    @computed_field
    @property
    def ndjson_file(self) -> Path:
        return self.log_dir / 'amherst.ndjson'

    @model_validator(mode='after')
    def set_templates(self):
        if self.templates is None:
            self.templates = Jinja2Templates(directory=self.template_dir)
            self.templates.env.filters['jsonable'] = make_jsonable
            self.templates.env.filters['urlencode'] = lambda value: quote(str(value))
            self.templates.env.filters['sanitise_id'] = sanitise_id
            self.templates.env.filters['ordinal_dt'] = ordinal_dt

        return self

    @_p.model_validator(mode='after')
    def create_log_files(self):
        self.log_dir.mkdir(parents=True, exist_ok=True)
        for v in (self.log_file, self.ndjson_file):
            if not v.exists():
                v.touch()
        return self

    model_config = SettingsConfigDict(env_file=load_env())


@lru_cache
def amherst_settings() -> Settings:
    res = Settings()


# logger = get_loguru(log_file=amherst_settings().log_file, profile='local', level=amherst_settings().log_level)
# def get_log():
#     log_file = os.environ['AMHERST_ENV']['LOG_FILE']


