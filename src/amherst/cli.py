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

from jinja2.utils import url_quote
from loguru import logger
from thefuzz import fuzz

from amherst.ui_runner import run_desktop_ui
from amherst.models.commence_adaptors import CategoryName

SCORER = fuzz.partial_ratio


class Mode(StrEnum):
    SHIP_BY_SRCH = 'ship_by_srch'
    SHIP_CONTENT = 'ship_content'
    NONE = 'none'


MODE = Mode.SHIP_BY_SRCH
# MODE = Mode.SHIP_CONTENT
# MODE = Mode.NONE


async def get_url_suffix2(category, pk, mode=MODE):
    match mode:
        case Mode.SHIP_BY_SRCH:
            return f'ship/form2?csrname={url_quote(category)}&pk_value={url_quote(pk)}&condition=equal&max_rtn=1'
        case Mode.SHIP_CONTENT:
            return f'ship/form_content2?csrname={url_quote(category)}&pk_value={url_quote(pk)}&condition=equal&max_rtn=1'
        case Mode.NONE:
            return ''


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=CategoryName, choices=list(CategoryName))
    arg_parser.add_argument('record_name', type=str)
    args = arg_parser.parse_args()
    if args.category.lower() == 'trial':
        args.category = 'radio trial'
    args.category = CategoryName(args.category.title())
    return args


async def main(category: CategoryName, record_name: str, mode: Mode = MODE):
    logger.warning('hastily removed filterarray from cursor')
    # logger.info(f'Starting Shipper searching for {category} record: {record_name}')
    # search_request = SearchRequest(
    #     csrname=category,
    #     pk_value=record_name,
    #     filtered=False,
    #     condition=ConditionType.EQUAL,
    #     max_rtn=1,
    # )
    # with pycommence_context(category) as pycmc:
    #     search_response = await pycommence_search(search_request, pycmc)
    # # search_response = await pycommence_response(search_request)
    # row = search_response
    # row = await parse_response(search_response)
    # url_suffix = await get_url_suffix(row, mode)
    url_suffix = await get_url_suffix2(category, record_name)
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
