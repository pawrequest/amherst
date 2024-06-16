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

from flaskwebgui import FlaskUI, close_application
from loguru import logger
from win32com.universal import com_error

from amherst.models.am_record import AmherstRecord, AmherstRecordIn
from pycommence import PyCommence
from amherst.am_config import am_sett
from amherst.models import am_record, db_models
from amherst import am_db, app_file
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressTemporary
from shipaw.models.pf_msg import Alert, Alerts
from shipaw.models.pf_shipment import ShipmentRequest


def split_reference_numbers(record: AmherstRecord):
    customer_str = record.customer
    reference_numbers = {}

    for i in range(1, 6):
        start_index = (i - 1) * 24
        end_index = i * 24
        if start_index < len(customer_str):
            reference_numbers[f'reference_number{i}'] = customer_str[start_index:end_index]
        else:
            break
    return reference_numbers


def amherst_shipment_request(
        record: AmherstRecord,
        el_client: ELClient or None = None
) -> ShipmentRequest:
    el_client = el_client or ELClient()
    ref_nums = split_reference_numbers(record)
    try:
        chosen_address = el_client.choose_address(record.input_address())
    except Exception as e:
        logger.exception(e)
        chosen_address = AddressTemporary.model_validate(
            record.input_address(),
            from_attributes=True
        )
    return ShipmentRequest(
        recipient_contact=record.contact(),
        recipient_address=chosen_address,
        shipping_date=record.send_date,
        total_number_of_parcels=record.boxes,
        **ref_nums,
    )


def parse_arguments():
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('category', type=str)
    arg_parser.add_argument('record_name', type=str)
    return arg_parser.parse_args()


async def main(category: am_record.AmherstTableEnum, record_name: str):
    # CoInitialize()
    alert = None
    # booking = None
    am_db.create_db()
    print("Template directory:", os.path.abspath(am_sett().base_dir / 'front' / 'templates'))

    try:
        with PyCommence.from_table_name_context(table_name=category) as py_cmc:
            record = py_cmc.one_record(record_name)
        record['cmc_table_name'] = category
        amrec = await cmc_record_to_amrec(record)
        booking = await amrec_to_booking(amrec)

        with am_db.get_session_cm() as session:
            session.add(booking)
            session.commit()
            session.refresh(booking)
            ...

        # try:
        # except ValidationError as e:
        #     msg = f'Error validating record, using partial data'
        #     logger.warning(f'{msg} \n{e}')
        #     amrec = AmherstRecordPartial(**record)
        #     amrec.alerts = [Alert(code=None, message=msg, type='WARNING')]

        # amrec = amrec.model_validate(amrec)

        # shiprec_id = am_db.amherst_record_to_shiprec(amrec)
        # assert shiprec_id, f'Error creating ShipableRecord for {amrec.name}'
        # logger.info(f'added ShipmentRecord #{shiprec_id}')

    except com_error as e:
        alert = 'Error: Commence Server execution failed. Ensure Commence is running.'

    except Exception as e:
        alert = f'Error creating ShipableRecord: {e}'
        raise

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


async def amrec_to_booking(amrec):
    booking = db_models.BookingStateDB(
        record=amrec,
        shipment_request=(amherst_shipment_request(amrec)),
        alerts=Alerts(alert=[Alert(code=None, message='Created')])
    )
    return booking


async def cmc_record_to_amrec(record):
    amrec_in = AmherstRecordIn(**record)
    amrec_in = amrec_in.model_validate(amrec_in)
    amrec = AmherstRecord(**amrec_in.model_dump())
    return amrec


if __name__ == '__main__':
    args = parse_arguments()
    asyncio.run(main(args.category, args.record_name))

    # main(args.category, args.record_name)
