import os
import re
import sys

# from entities.const import DFLT
from ..dflt import DFLT_PATHS

REAL_INV_FOLDER = r'R:\ACCOUNTS\invoices'


def main():
    print(next_inv_num())
    input('Press Enter to close...')
    sys.exit(0)


if __name__ == '__main__':
    main()


def next_inv_num(inv_dir=DFLT_PATHS.INV_DIR):
    inv_dir = inv_dir if inv_dir.exists() else DFLT_PATHS.INV_DIR_MOCK
    inv_numbers = list(get_inv_nums(inv_dir))
    if not inv_numbers:
        return 'A00001'
    inv_numbers = sorted(inv_numbers, reverse=True)
    for index, num in enumerate(inv_numbers):
        if has_20_after(index=index, nums=inv_numbers):
            new_num = f'{num + 1}'.zfill(5)
            new_filename = f'A{new_num}'
            return new_filename
    else:
        new_num = f'{max(inv_numbers) + 1}'.zfill(5)
        return f'A{new_num}'


def get_inv_nums(inv_dir) -> set[int]:
    files = os.listdir(inv_dir)
    pattern = re.compile(r'^[Aa](\d{5}).*$')
    matching_files = [f.lower() for f in files if pattern.match(f)]
    inv_numbers = {int(pattern.match(f).group(1)) for f in matching_files}
    return inv_numbers


def has_20_after(index: int, nums: {int}):
    if len(nums) < 20:
        return False
    tally = 0
    while tally < 20:
        if index + 1 < len(nums):
            num = nums[index]
            next_num = nums[index + 1]
            if num == next_num + 1:
                tally += 1
                index += 1
            else:
                return False
        else:
            return False
    return True
