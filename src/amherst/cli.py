"""
Wrap FastAPI app in FlaskWebGUI for desktop application.
Use `Paw Request fork <https://github.com/pawrequest/flaskwebgui>`_ for URL_SUFFIX to dynamically set loading page to the retrieved record

Environment variables:
    AM_ENV: Path to environment file defining:
        # - sql database location
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
from amherst.back.search_paginate import SearchRequest, SearchResponse
from amherst.models.amherst_models import AmherstTableBase
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
    logger.info(f'Starting Shipper searching for {category} record: {record_name}')
    search_request = SearchRequest(
        csrname=category,
        pk_value=record_name,
        filtered=False,
    )
    search_response = await pycommence_response(search_request)
    url_suffix = await parse_response(search_response)
    await run_desktop_ui(url_suffix)


async def parse_response(res: SearchResponse):
    if res.length == 0:
        raise ValueError(f'No {res.search_request.csrname} record found for {res.search_request.pk_value}')
    elif res.length == 1 or res.search_request.pk_value == 'Test':
        row = res.records[0]
    else:
        raise NotImplementedError(f'Multiple {res.search_request.csrname} records found for {res.search_request.pk_value}')

    url_suffix = get_url_suffix(row)
    return url_suffix


def get_url_suffix(record: AmherstTableBase):
    return f'ship/row_id/{record.category}/{record.row_id}'


if __name__ == '__main__':
    args = parse_arguments()
    asyncio.run(main(args.category, args.record_name))
