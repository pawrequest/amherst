# /// script
# requires-python = ">=3.13"
# dependencies = [
# "amherst-core @ git+https://github.com/pawrequest/amherst-core",
# "pycommence @ git+https://github.com/pawrequest/pycommence@v3",
# ]
# ///
import argparse
import sys
from argparse import Namespace
from pathlib import Path

from amherst_core.models import AmherstHire
from pycommence import PyCommence


def parse_args():
    parser = argparse.ArgumentParser(description='Add Amherst Repair Excel Workbook')
    parser.add_argument('--record', type=str, required=True, help='Amherst Repair Record Name')
    parser.add_argument('--output', type=Path, required=True, help='Repair Sheet Storage Dir')
    parser.add_argument('--template_workbook', type=Path, required=True, help='Repair Sheet Storage Dir')
    return parser.parse_args()


def main(args: Namespace | None = None) -> int:
    args = args or parse_args()
    record_name = args.record
    excel_dir = args.output
    excel_file = excel_dir / f'{record_name}.xlsx'
    with PyCommence('Repairs') as p:
        record = p.item_read_csr(pk=record_name)
    if excel_file.exists():
        raise FileExistsError(f'Excel file already exists: {excel_file}')
    print(record)
    input('Press Enter to continue...')
    return 0


if __name__ == '__main__':
    temp_dir = Path(__file__).parent.parent.parent / 'temp' / 'repair_excel'
    temp_dir.mkdir(parents=True, exist_ok=True)
    template = temp_dir / 'template.xlsx'
    test_args = Namespace(record='TEST28012025', output=temp_dir, template=template)
    sys.exit(main(test_args))
