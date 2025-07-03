import argparse
import os
import sys


def print_file(filepath):
    try:
        os.startfile(filepath, 'print')
        print(f'Printing {filepath}')
    except Exception as e:
        print(f'Error: {e}')


def main():
    parser = argparse.ArgumentParser(description='Print a file using the default printer.')
    parser.add_argument('file_path', type=str, help='Path to the file to print')
    args = parser.parse_args()
    file_path = args.file_path
    if not os.path.exists(file_path):
        print(f'File not found: {file_path}')
        sys.exit(1)
    print_file(file_path)


if __name__ == '__main__':
    main()
