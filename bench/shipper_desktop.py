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
import base64
import os

from combadge.core.errors import BackendError
from flaskwebgui import FlaskUI, close_application
from loguru import logger
from win32com.universal import com_error
from thefuzz import fuzz

import amherst.commence_adaptors
from amherst.db import create_db, get_session_cm
from amherst.config import settings
from amherst import app_file
from amherst.models.am_record_smpl import AmherstTableDB
from pycommence.pycommence_v2 import PyCommence

from amherst.models import commence_adaptors

SCORER = fuzz.partial_ratio


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=str)
    arg_parser.add_argument('record_name', type=str)
    return arg_parser.parse_args()


async def main(category: commence_adaptors.CsrName, record_name: str):
    logger.info(f'Starting Shipper with {category} record: {record_name}')
    alert = None
    create_db()
    print('Template directory:', os.path.abspath(settings().base_dir / 'front' / 'templates'))
    booking = None

    try:
        pycmc = PyCommence.with_csr(category)
        record: dict[str, str] = pycmc.one_record(record_name, category)
        record['category'] = category

        amrec: AmherstTableDB = AmherstTableDB.from_dict(record)

    except BackendError:
        alert = 'Backend Error. Likely Address details are conflicted (wrong postcode?).'

    except com_error:
        alert = 'Error: Commence Server execution failed. Ensure Commence is running.'

    else:
        try:
            booking = await amrec_to_booking(amrec)

            with get_session_cm() as session:
                session.add(booking)
                session.commit()
                session.refresh(booking)
                ...
        except Exception as e:
            alert = f'Error creating ShipableRecord: {e}'

    try:
        if alert:
            logger.exception(alert)
            alert = base64.urlsafe_b64encode(alert.encode('utf-8')).decode('utf-8')
            fui = FlaskUI(
                fullscreen=True,
                app=app_file.app,
                server='fastapi',
                url_suffix=f'fail/{alert}',
            )
        else:
            fui = FlaskUI(
                fullscreen=True,
                app=app_file.app,
                server='fastapi',
                url_suffix=f'{booking.id}',
                # url_suffix=f'ship/select/{shiprec_id}',
            )
        fui.run()
    except Exception as e:
        if "got an unexpected keyword argument 'url_suffix'" in str(e):
            msg = (
                'URL_SUFFIX is not compatible with this version of FlaskWebGui'
                'Install PawRequest/flaskwebgui from  @ git+https://github.com/pawrequest/flaskwebgui'
            )
            logger.exception(msg)
            raise ImportError(msg)
        else:
            raise
    finally:
        close_application()


if __name__ == '__main__':
    args = parse_arguments()
    asyncio.run(main(args.category, args.record_name))

    # main(args.category, args.record_name)
