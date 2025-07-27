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

from amherst.set_env import set_amherstpr_env
from amherst.models.commence_adaptors import CategoryName


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=CategoryName, choices=list(CategoryName))
    arg_parser.add_argument('record_name', type=str)
    arg_parser.add_argument('--sandbox', action='store_true', help='Run in sandbox mode')
    args = arg_parser.parse_args()
    set_amherstpr_env(sandbox=args.sandbox)
    if 'trial' in args.category.name.lower():
        args.category = CategoryName.Trial
    args.category = CategoryName(args.category.title())
    return args


ARGS = parse_arguments()

from amherst.ui_runner import run_desktop_ui  # after setting env

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
        # case Mode.SHIP_CONTENT:
        #     return (
        #         f'ship/form_content2?csrname={url_quote(category)}&pk_value={url_quote(pk)}&condition=equal&max_rtn=1'
        #     )
        case Mode.NONE:
            return ''
    return None


async def main(category: CategoryName, record_name: str, mode: Mode = MODE):
    url_suffix = await get_url_suffix2(category, record_name)
    await run_desktop_ui(url_suffix)


# async def parse_response(res):
#     if res.length == 1 or res.search_request.pk_value == 'Test':
#         return res.records[0]
#     elif res.length == 0:
#         raise ValueError(f'No {res.search_request.csrname} record found for {res.search_request.pk_value}')
#     else:
#         raise NotImplementedError(
#             f'Multiple {res.search_request.csrname} records found for {res.search_request.pk_value}'
#         )


def main_cli():
    asyncio.run(main(ARGS.category, ARGS.record_name))


if __name__ == '__main__':
    main_cli()
