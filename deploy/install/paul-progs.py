import argparse
import os
import shutil
import subprocess
from pathlib import Path

APP_NAME = 'paul_r'
PROGS_SRC = Path(__file__).parent.parent / 'progs'
DATA_DIR = Path(os.getenv('LOCALAPPDATA')) / APP_NAME
PROGS_TGT = Path(rf'C:\Program Files\{APP_NAME}\progs')
# PROGS_TGT = Path(rf'{DATA_DIR}\progs')

ADDITIONAL_FILES_TO_COPY = {
}


def getargs():
    parser = argparse.ArgumentParser(description='Splash screen for Amherst')
    parser.add_argument('--version', action='store_true', help='Display version information')
    return parser.parse_args()


def install_uv():
    try:
        subprocess.run(['winget', 'install', '--id=astral-sh.uv', '-e'], check=True)
        print('UV installed successfully.')
    except subprocess.CalledProcessError as e:
        print(f'An error occurred while installing UV: {e}')


def maybe_install_uv():
    local_apps_dir = Path(os.getenv('LOCALAPPDATA'))
    if Path.exists(local_apps_dir / 'uv'):
        print('UV is already installed.')
    else:
        install_uv()


def copy_files1(maindir: Path, files_to_copy: dict = None):
    files_to_copy = files_to_copy or {}
    for file, dest in files_to_copy.items():
        dest = Path(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(file, dest)
    pass


def copy_files(src_dir: Path, tgt_dir: Path, files_to_copy: dict = None):
    if src_dir.is_dir():
        print(f'Copying {src_dir} to {tgt_dir}')
        shutil.copytree(src_dir, tgt_dir, dirs_exist_ok=True)
    else:
        print(f'{src_dir} is not a directory. Skipping.')

    if files_to_copy:
        print(f'Copying additional files to {tgt_dir}')
        for file, dest in files_to_copy.items():
            print(f'Copying {file} to {dest}')
            dest = Path(dest)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(file, dest)


def main(args=None):
    if args is None:
        args = getargs()

    maybe_install_uv()
    copy_files(PROGS_SRC, PROGS_TGT, ADDITIONAL_FILES_TO_COPY)


if __name__ == '__main__':
    main()
