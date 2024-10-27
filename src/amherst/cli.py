"""
Wrap FastAPI app in FlaskWebGUI for desktop application.
Use `Paw Request fork <https://github.com/pawrequest/flaskwebgui>`_ for URL_SUFFIX to dynamically set loading page to the retrieved record

Environment variables:
    AM_ENV: Path to environment file defining:
        - log file location
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

from amherst.back.backend_pycommence import pycommence_context, pycommence_search
from amherst.back.backend_search_paginate import SearchRequest
from amherst.models.amherst_models import AmherstTableBase
from amherst.ui_runner import run_desktop_ui
from amherst.models.commence_adaptors import AmherstTableName
from pycommence.filters import ConditionType

SCORER = fuzz.partial_ratio


class Mode(StrEnum):
    SHIP_BY_SRCH = 'ship_by_srch'


MODE = Mode.SHIP_BY_SRCH


async def get_url_suffix(record: AmherstTableBase, mode: Mode = MODE):
    # todo parse mode
    return f'ship/form/{record.category}?row_id={record.row_id}'


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
        condition=ConditionType.EQUAL,
        max_rtn=1,
    )
    with pycommence_context(category) as pycmc:
        search_response = await pycommence_search(search_request, pycmc)
    # search_response = await pycommence_response(search_request)
    row = await parse_response(search_response)
    url_suffix = await get_url_suffix(row, mode)
    await run_desktop_ui(url_suffix)


async def parse_response(res):
    if res.length == 1 or res.search_request.pk_value == 'Test':
        return res.records[0]
    elif res.length == 0:
        raise ValueError(f'No {res.search_request.csrname} record found for {res.search_request.pk_value}')
    else:
        raise NotImplementedError(
            f'Multiple {res.search_request.csrname} records found for {res.search_request.pk_value}'
        )


if __name__ == '__main__':
    args = parse_arguments()
    asyncio.run(main(args.category, args.record_name))
