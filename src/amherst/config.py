from __future__ import annotations

import functools
import os
import re
from datetime import date, datetime
from pathlib import Path
import sys
import typing as _t
from urllib.parse import quote
from starlette.templating import Jinja2Templates

import pydantic as _p
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from pawlogger import get_loguru

from amherst.set_env import get_envs_dir


class Settings(BaseSettings):
    # db_loc: Path
    log_file: Path
    src_dir: Path = Path(__file__).resolve().parent
    # src_dir: _t.Annotated[Path, _p.BeforeValidator(set_src_dir)] = None
    # data_dir: Path = Path(__file__).parent / '_data'
    templates: Path | None = None
    log_level: str = 'INFO'
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


def make_jsonable(pyd_model: BaseModel) -> dict:
    thedict = pyd_model.model_dump()
    return jsonable_encoder(thedict)


def date_int_w_ordinal(n):
    return str(n) + ('th' if 4 <= n % 100 <= 20 else {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th'))


def ordinal_dt(dt: datetime | date) -> str:
    return dt.strftime(f'%a {date_int_w_ordinal(dt.day)} %b %Y')


TEMPLATES = Jinja2Templates(directory=str(AM_SETTINGS.src_dir / 'front' / 'templates'))
TEMPLATES.env.filters['jsonable'] = make_jsonable
TEMPLATES.env.filters['urlencode'] = lambda value: quote(str(value))
TEMPLATES.env.filters['sanitise_id'] = sanitise_id
TEMPLATES.env.filters['ordinal_dt'] = ordinal_dt
