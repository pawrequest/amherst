import argparse
from pathlib import Path
import pandas as pd

AC_FILE = Path(r'R:\ACCOUNTS\ye2025\ac2425.xls')


def get_ac_file(ac_file_loc: Path = AC_FILE) -> pd.DataFrame:
    with open(ac_file_loc, 'rb') as ac_file:
        df = pd.read_excel(ac_file, header=2)
    return df


AC_DF = get_ac_file()


def get_status(inv_num: str, df: pd.DataFrame = AC_DF) -> str:
    rs = df.loc[df['No.'] == inv_num, 'Status'].values
    return rs[0] if rs else 'Not Found'


def invoice_num_from_path(inv_path: str):
    return Path(inv_path).stem


def payment_status_cli():
    parser = argparse.ArgumentParser(description='Check invoice payment status')
    parser.add_argument('invoice_number', type=str, help='Invoice number to check')
    parser.add_argument(
        'accounts_spreadsheet', type=Path, help='Path to accounts spreadsheet', nargs='?', default=AC_DF
    )
    args = parser.parse_args()
    inv_num = invoice_num_from_path(args.invoice_number)
    print(get_status(inv_num))
