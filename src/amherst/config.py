from __future__ import annotations

import functools
import os
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

AM_ENV = os.getenv('AM_ENV')
if not AM_ENV:
    raise ValueError('AM_ENV environment variable not set')
if not Path(AM_ENV).exists():
    raise ValueError(f'{AM_ENV} .env file does not exist: {AM_ENV}')


def set_src_dir(v, values):
    # pyinstaller compatibility
    if v is None:
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # noinspection PyProtectedMember
            return Path(sys._MEIPASS)
        else:
            return Path(__file__).resolve().parent


class Settings(BaseSettings):
    """Set by env file at location specified by AM_ENV."""

    # db_loc: Path
    log_file: Path
    src_dir: _t.Annotated[Path, _p.BeforeValidator(set_src_dir)] = None
    # data_dir: Path = Path(__file__).parent / '_data'
    templates: Path | None = None

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

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=AM_ENV)


@functools.lru_cache
def settings():
    return Settings()


logger = get_loguru(log_file=settings().log_file, profile='local', level='DEBUG')


def make_jsonable(pyd_model: BaseModel) -> dict:
    thedict = pyd_model.model_dump()
    return jsonable_encoder(thedict)


logger.info('\n' + '\n'.join([f'{k.upper()} = {v}' for k, v in settings().model_dump().items()]))
TEMPLATES = Jinja2Templates(directory=str(settings().src_dir / 'front' / 'templates'))
TEMPLATES.env.filters['jsonable'] = make_jsonable
# TEMPLATES.env.filters['urlencode'] = quote
TEMPLATES.env.filters['urlencode'] = lambda value: quote(str(value))
