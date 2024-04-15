import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

DATA_DIR = Path(__file__).parent / '_data'


class AmSettings(BaseSettings):
    parcelforce_labels_dir: Path = DATA_DIR / 'parcelforce_labels'
    db_loc: Path = DATA_DIR / 'amherst.db'
    log_file: Path = DATA_DIR / 'amherst.log'

    model_config = SettingsConfigDict(env_ignore_empty=True, env_file=os.getenv('AM_ENV'))


am_settings = AmSettings()