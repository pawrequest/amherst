from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    pf_ac_num_1: str
    pf_ac_num_2: str
    pf_cont_num_1: str
    pf_cont_num_2: str
    pf_expr_usr: str
    pf_expr_pwd: str
    pf_wsdl: str

    ship_live: bool = False
    pf_binding: str = '{http://www.parcelforce.net/ws/ship/v14}ShipServiceSoapBinding'
    pf_endpoint: str = 'https://expresslink-test.parcelforce.net/ws/'

    db_loc: str = 'amherst.db'
    parcelforce_labels_dir: str

    model_config = SettingsConfigDict(env_ignore_empty=True)
