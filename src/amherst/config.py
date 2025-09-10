from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from urllib.parse import quote

import pydantic as _p
from fastapi.encoders import jsonable_encoder
from pawlogger import get_loguru
from pydantic_settings import BaseSettings, SettingsConfigDict
from starlette.templating import Jinja2Templates

from amherst.set_env import get_envs_dir


class Settings(BaseSettings):
    log_file: Path
    src_dir: Path = Path(__file__).resolve().parent
    templates: Path | None = None
    log_level: str = 'DEBUG'
    sandbox: bool = False

    @_p.field_validator('templates', mode='after')
    def set_templates(cls, v, values):
        if not v:
            return Jinja2Templates(directory=str(values.data['src_dir'] / 'front' / 'templates'))
        return v

    @_p.field_validator('log_file', mode='after')
    def path_exists(cls, v, values):
        if not v.parent.exists():
            v.parent.mkdir(parents=True, exist_ok=True)
        if not v.exists():
            v.touch(exist_ok=True)
        return v

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=get_envs_dir() / 'am.env', extra='ignore')


AM_SETTINGS = Settings()

logger = get_loguru(log_file=AM_SETTINGS.log_file, profile='local', level=AM_SETTINGS.log_level)


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


TEMPLATES = Jinja2Templates(directory=str(AM_SETTINGS.src_dir / 'front' / 'templates'))
TEMPLATES.env.filters['jsonable'] = make_jsonable
TEMPLATES.env.filters['urlencode'] = lambda value: quote(str(value))
TEMPLATES.env.filters['sanitise_id'] = sanitise_id
TEMPLATES.env.filters['ordinal_dt'] = ordinal_dt
