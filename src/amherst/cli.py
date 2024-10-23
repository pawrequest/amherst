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

from amherst.back.backend_pycommence import pycommence_response
from amherst.back.search_paginate import SearchRequest
from amherst.ui_runner import run_desktop_ui
from amherst.models.commence_adaptors import AmherstTableName

SCORER = fuzz.partial_ratio


class Mode(StrEnum):
    SHIP_BY_SRCH = 'ship_by_srch'


MODE = Mode.SHIP_BY_SRCH


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=AmherstTableName, choices=list(AmherstTableName))
    arg_parser.add_argument('record_name', type=str)
    args = arg_parser.parse_args()
    if args.category.lower() == 'trial':
        args.category = 'radio trial'
    args.category = AmherstTableName(args.category.title())
    return args


async def main(category: AmherstTableName, record_name: str, mode: Mode = MODE):
    logger.info(f'Starting Shipper with {category} record: {record_name}')
    req = get_req(category, record_name)
    res = await get_res(req)
    if res.length == 0:
        raise ValueError(f'No record found for {record_name=}')
    elif res.length == 1 or record_name == 'Test':
        row = res.records[0]
        url_suffix = get_url2(category, row.row_id)
    else:
        logger.error(f'Multiple records found for {record_name=}')
        url_suffix = 'MULTIPLE_RECORDS_FOUND'
    await run_desktop_ui(url_suffix)


def get_req(category, record_name):
    return SearchRequest(
        csrname=category,
        pk_value=record_name,
    )


async def get_res(req: SearchRequest):
    return await pycommence_response(req)


# def get_url(mode: Mode, category, record_name):
#     # todo 'refs' from cmc ARE NOT UNIQUE (lol)
#     srch_term = get_ref(record_name)
#     logger.debug(f'{srch_term=}')
#     match mode:
#         case Mode.SHIP_BY_SRCH:
#             url_suffix = f'ship/pk/{category}/{srch_term}?filtered=False'
#         case _:
#             raise ValueError(f'Unknown mode: {mode}')
#     return url_suffix


def get_url2(category, row_id):
    return f'ship/row_id/{category}/{row_id}'


if __name__ == '__main__':
    args = parse_arguments()
    asyncio.run(main(args.category, args.record_name))
