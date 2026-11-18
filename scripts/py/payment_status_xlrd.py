# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "pandas",
#   "xlrd",
# ]
# ///
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


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('invoice_path', type=str, help='Path to the invoice file')
    parser.add_argument('accounts_file', type=Path, help='Path to the accounts file')
    args = parser.parse_args()
    invoice_num = invoice_num_from_path(args.invoice_path)
    status = get_payment_status(invoice_num, args.accounts_file)
    print(f'Payment status for invoice {invoice_num}: {status}')
    inp = input('Enter to close')
