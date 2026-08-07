# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "pyperclip",
# ]
# ///
import os
import re

REAL_INV_FOLDER = r'R:\ACCOUNTS\invoices'
INV_NAME_RE = re.compile(r'^A(\d{5})\.(?:doc|pdf)$', re.IGNORECASE)


def next_inv_num(inv_dir=REAL_INV_FOLDER):
    inv_numbers = get_inv_nums(inv_dir)
    if not inv_numbers:
        return f'no invoices found in {inv_dir}'

    for num in sorted(inv_numbers, reverse=True):
        candidate = num + 1
        if not has_20_before(candidate_num=candidate, nums=inv_numbers):
            continue
        if candidate in inv_numbers:
            continue
        if invoice_name_exists(inv_dir=inv_dir, inv_num=candidate):
            continue
        return f'A{candidate:05d}'

    return 'no valid next invoice number found'


def get_inv_nums(inv_dir) -> set[int]:
    files = os.listdir(inv_dir)
    inv_numbers = set()
    for file_name in files:
        match = INV_NAME_RE.match(file_name)
        if match:
            inv_numbers.add(int(match.group(1)))
    return inv_numbers


def has_20_before(candidate_num: int, nums: set[int], count: int = 20) -> bool:
    """True when the previous `count` invoice numbers all exist."""
    return all((candidate_num - offset) in nums for offset in range(1, count + 1))


def invoice_name_exists(inv_dir: str, inv_num: int) -> bool:
    base_name = f'A{inv_num:05d}'
    return any(
        os.path.exists(os.path.join(inv_dir, f'{base_name}{ext}'))
        for ext in ('.doc', '.pdf')
    )


if __name__ == '__main__':
    import argparse
    import sys

    parser = argparse.ArgumentParser()
    parser.add_argument('--pause', type=bool, nargs='?', const=True, default=False)
    parser.add_argument('--clip', type=bool, nargs='?', const=True, default=True)
    args = parser.parse_args()

    num = next_inv_num()
    if args.clip:
        import pyperclip

        pyperclip.copy(num)
    print(num)
    if args.pause:
        input('(Copied to clipboard) Press Enter to continue...')
    sys.exit(0)
