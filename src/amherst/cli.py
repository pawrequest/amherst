import argparse
import asyncio

from amherst_core.consts_enums import CategoryName
from loguru import logger

from amherst.run_ng import nice_shipper
from amherst.ui_runner import run_shipper


def parse_ship_args():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=CategoryName, choices=list(CategoryName))
    arg_parser.add_argument('record_name', type=str)
    args = arg_parser.parse_args()
    return args


def shipper_cli():
    args = parse_ship_args()
    logger.info(f'starting shipper for {args.category} {args.record_name}')

    # asyncio.run(pycommence_shipper(args.category, args.record_name))
    asyncio.run(run_shipper(args.category, args.record_name))


def nice_cli():
    args = parse_ship_args()
    logger.info(f'starting shipper for {args.category} {args.record_name}')

    nice_shipper(args.category, args.record_name)


if __name__ == '__main__':
    shipper_cli()
