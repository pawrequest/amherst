from __future__ import annotations

import os
from functools import lru_cache
from importlib.resources import files
from pathlib import Path

import pydantic as _p
from dotenv import dotenv_values, load_dotenv
from pawlogger import get_loguru
from pydantic import computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.templating import Jinja2Templates


def load_env_index(envs_index: Path) -> None:
    load_dotenv(envs_index)
    for env in ('AMHERST_ENV',):
    # for env in ('SHIPAW_ENV', 'AMHERST_ENV'):
        if not os.getenv(env):
            raise ValueError(f'Environment variable {env} not set in {envs_index}')
        if not Path(os.getenv(env)).exists():
            raise ValueError(f'Environment variable {env} points to non-existent file {os.getenv(env)}')
        getlog()


def getlog():
    env_values = dotenv_values(Path(os.getenv('AMHERST_ENV')))
    log_dir = Path(env_values.get('LOG_DIR'))
    if not log_dir:
        raise ValueError('LOG_DIR not set in AMHERST_ENV')
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'amherst.log'
    log_file.touch(exist_ok=True)
    log_level = env_values.get('LOG_LEVEL') or 'DEBUG'
    get_loguru(log_file=log_file, profile='local', level=log_level)


def load_env() -> Path:
    ei = Path(os.environ.get('ENV_INDEX', ''))
    if not ei or not ei.exists():
        raise ValueError('ENV_INDEX not set or does not exist')
    load_env_index(ei)
    print(f'Loading env index from {ei}')
    amherst_env = Path(os.getenv('AMHERST_ENV'))
    print(f'Loading Amherst Settings from {amherst_env}')
    return amherst_env


class Settings(BaseSettings):
    log_dir: Path
    log_level: str = 'DEBUG'
    ui_dir: Path = files('amherst').joinpath('ui')
    templates: Jinja2Templates | None = None
    data_dir: Path = files('amherst').joinpath('data')

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
            # self.templates.env.filters['jsonable'] = make_jsonable
            # self.templates.env.filters['urlencode'] = lambda value: quote(str(value))
            # self.templates.env.filters['sanitise_id'] = sanitise_id
            # self.templates.env.filters['ordinal_dt'] = ordinal_dt

        return self

    @_p.model_validator(mode='after')
    def create_log_files(self):
        self.log_dir.mkdir(parents=True, exist_ok=True)
        for v in (self.log_file, self.ndjson_file):
            if not v.exists():
                v.touch()
        return self

    model_config = SettingsConfigDict()


@lru_cache
def amherst_settings() -> Settings:
    res = Settings(_env_file=load_env())
    return res

# logger = get_loguru(log_file=amherst_settings().log_file, profile='local', level=amherst_settings().log_level)
# def get_log():
#     log_file = os.environ['AMHERST_ENV']['LOG_FILE']
