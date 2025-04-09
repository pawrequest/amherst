from __future__ import annotations

import functools
import os
import re
from datetime import date, datetime
from pathlib import Path
import sys
import typing as _t
from urllib.parse import quote

import pydantic as _p
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pawlogger import get_loguru
from starlette.templating import Jinja2Templates


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


set_sandbox_env()


def set_src_dir(v, values):
    # pyinstaller compatibility
    if v is None:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # noinspection PyProtectedMember
            return Path(sys._MEIPASS)
        else:
            return Path(__file__).resolve().parent


def src_dir_no_exec(v, values):
    return Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Set by env file at location specified by AM_ENV."""

    # db_loc: Path
    log_file: Path
    src_dir: _t.Annotated[Path, _p.BeforeValidator(set_src_dir)] = None
    # data_dir: Path = Path(__file__).parent / '_data'
    templates: Path | None = None
    log_level: str = 'INFO'

    @_p.field_validator('templates', mode='after')
    def set_templates(cls, v, values):
        if not v:
            return Jinja2Templates(directory=str(values.data['src_dir'] / 'front' / 'templates'))
        return v

    # @cached_property
    # def db_url(self):
    #     return f'sqlite:///{self.db_loc.as_posix()}'

    # @_p.field_validator('db_loc', 'log_file', mode='after')
    @_p.field_validator('log_file', mode='after')
    def path_exists(cls, v, values):
        if not v.parent.exists():
            v.parent.mkdir(parents=True, exist_ok=True)
        if not v.exists():
            v.touch(exist_ok=True)
        return v

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=AMHERSTPR / 'am.env', extra='ignore')


@functools.lru_cache
def settings():
    return Settings()


logger = get_loguru(log_file=settings().log_file, profile='local', level=settings().log_level)


def sanitise_id(value):
    return re.sub(r'\W|^(?=\d)', '_', value).lower()


def make_jsonable(pyd_model: BaseModel) -> dict:
    thedict = pyd_model.model_dump()
    return jsonable_encoder(thedict)


def date_int_w_ordinal(n):
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def ordinal_dt(dt: datetime | date) -> str:
    return dt.strftime(f'%a {date_int_w_ordinal(dt.day)} %b %Y')


TEMPLATES = Jinja2Templates(directory=str(settings().src_dir / 'front' / 'templates'))
TEMPLATES.env.filters['jsonable'] = make_jsonable
TEMPLATES.env.filters['urlencode'] = lambda value: quote(str(value))
TEMPLATES.env.filters['sanitise_id'] = sanitise_id
TEMPLATES.env.filters['ordinal_dt'] = ordinal_dt
