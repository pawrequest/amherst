from pathlib import Path
import pandas as pd


def load_accounts_df(accounts_file: Path) -> pd.DataFrame:
    with open(accounts_file, 'rb') as accounts_file:
        df = pd.read_excel(accounts_file, header=2)
    return df


def get_payment_status(invoice_num: str, accounts_file: Path) -> str:
    df = load_accounts_df(accounts_file)
    rs = df.loc[df['No.'] == invoice_num, 'Status'].values
    return rs[0] if rs else 'Not Found'


def invoice_num_from_path(inv_path_str: str):
    return Path(inv_path_str).stem


