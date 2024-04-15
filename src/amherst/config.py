from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(r'R:\paul_r\.internal\envs\sandbox.env')


class Settings(BaseSettings):
    pf_ac_num_1: str
    pf_ac_num_2: str
    pf_cont_num_1: str
    pf_cont_num_2: str

    ship_live: bool = False
    pf_expr_usr: str
    pf_expr_pwd: str

    pf_wsdl: str
    pf_binding: str = '{http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding'
    pf_endpoint: str = 'https://expresslink-test.parcelforce.net/ws/'

    db_loc: str = 'amherst.db'
    parcelforce_labels_dir: str
    log_file: Path = Path(__file__).parent / 'amherst.log'

    model_config = SettingsConfigDict(env_ignore_empty=True)


settings = Settings()
...
