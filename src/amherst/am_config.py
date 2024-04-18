import os
from pathlib import Path

import pydantic as _p
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict

DATA_DIR = Path(__file__).parent / '_data'


class AmSettings(BaseSettings):
    parcelforce_labels_dir: Path
    db_loc: Path
    log_file: Path

    @_p.field_validator('db_loc', 'log_file', mode='after')
    def path_exists(cls, v, values):
        if not v.parent.exists():
            v.parent.mkdir(parents=True, exist_ok=True)
        if not v.exists():
            v.touch(exist_ok=True)
        return v

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=os.getenv('AM_ENV'))


AM_SETTINGS = AmSettings()
...

logger.info(f"AmSetting loaded from {AM_SETTINGS.model_config.get('env_file')}")
logger.info(AM_SETTINGS.model_dump_json())
