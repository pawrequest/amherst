"""
Wrap FastAPI app in FlaskWebGUI for desktop application.
Use `Paw Request fork <https://github.com/pawrequest/flaskwebgui>`_ for URL_SUFFIX to dynamically set loading page to the retrieved record

Environment variables:
    AM_ENV: Path to environment file defining:
        - sql database location
        - log file location
        - parcelforce labels directory
    SHIP_ENV: Path to environment file defining:
        - parcelforce account numbers
        - parcelforce contract numbers
        - parcelforce username and password
        - parcelforce wsdl
        - parcelforce endpoint
        - parcelforce binding
        - parcelforce live status

"""

from __future__ import annotations

import argparse
import asyncio
from enum import StrEnum

from loguru import logger
from thefuzz import fuzz


from amherst.fastui_runner import run_desktop_ui
from amherst.models.commence_adaptors import AmherstTableName, get_ref

SCORER = fuzz.partial_ratio


class Mode(StrEnum):
    SHIP_BY_SRCH = 'ship_by_srch'


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    # arg_parser.add_argument('category', type=str)
    arg_parser.add_argument('category', type=AmherstTableName, choices=list(AmherstTableName))
    arg_parser.add_argument('record_name', type=str)
    args = arg_parser.parse_args()
    if args.category.lower() == 'trial':
        args.category = 'radio trial'
    args.category = AmherstTableName(args.category.title())
    return args


async def main(category: AmherstTableName, record_name: str):
    logger.info(f'Starting Shipper with {category} record: {record_name}')
    url_suffix = get_url(Mode.SHIP_BY_SRCH, category, record_name)
    await run_desktop_ui(url_suffix)


def get_url(mode: Mode, category, record_name):
    srch_term = get_ref(record_name)
    logger.debug(f'{srch_term=}')
    match mode:
        case Mode.SHIP_BY_SRCH:
            url_suffix = f'ship/pk/{category}/{srch_term}?filtered=False'
        case _:
            raise ValueError(f'Unknown mode: {mode}')
    return url_suffix


if __name__ == '__main__':
    args = parse_arguments()
    asyncio.run(main(args.category, args.record_name))
