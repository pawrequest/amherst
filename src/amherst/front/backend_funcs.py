from __future__ import annotations

import time
import typing as _t
import pathlib

from sqlmodel import Session
from starlette.templating import Jinja2Templates
from suppawt.office_ps.email_handler import Email
from loguru import logger

from pycommence import PyCommence
from shipaw.expresslink_client import ELClient
from shipaw.models import pf_msg
from shipaw.models.pf_shipment import ShipmentRequest
from amherst.am_config import am_sett
from amherst.am_shared import HireFields
from amherst.models.am_record import AmherstRecord
from amherst.models.db_models import BookingStateDB
from shipaw.ship_types import ExpressLinkError

type EmailChoices = _t.Literal['invoice', 'label', 'missing_kit']


def book_shipment(el_client, shipment_request: ShipmentRequest) -> pf_msg.CreateShipmentResponse:
    resp = el_client.send_shipment_request(shipment_request)
    for a in resp.alerts.alert if resp.alerts else []:
        if a.type == 'ERROR':
            logger.error(f'ERROR IN BOOKING: {a.message}')
            raise ExpressLinkError(a.message)
        logger.warning(f'WARNING IN BOOKING: {a.message}')
    return resp


def record_tracking(booking_state: BookingStateDB):
    record = booking_state.record
    try:
        category = record.cmc_table_name
        if category == 'Customer':
            logger.error('CANT LOG TO CUSTOMER')
            return
        do_record_tracking(booking_state)
        logger.debug(f'Logged tracking for {category} {record.name}')

    except Exception as exce:
        logger.exception(exce)
        raise


def do_record_tracking(booking: BookingStateDB):
    tracking_link = booking.response.tracking_link()
    cmc_package = (
        {
            HireFields.TRACK_INBOUND: tracking_link,
            HireFields.ARRANGED_INBOUND: True,
            HireFields.PICKUP_DATE: f'{booking.shipment_request.shipping_date:%Y-%m-%d}',
        }
        if booking.direction in ['in', 'dropoff']
        else {HireFields.TRACK_OUTBOUND: tracking_link, HireFields.ARRANGED_OUTBOUND: True}
    )

    with PyCommence.from_table_name_context(table_name=booking.record.cmc_table_name) as py_cmc:
        py_cmc.edit_record(booking.record.name, row_dict=cmc_package)
    booking.tracking_logged = True
    logger.debug(f'Logged {str(cmc_package)} to Commence')


async def subject(invoice_num: str | None = None, missing=None, label=None):
    return (
        f'Amherst Radios'
        f'{f"- Invoice {invoice_num} Attached" if invoice_num else ""} '
        f'{"- We Are Missing Kit" if missing else ""} '
        f'{"- Shipping Label Attached" if label else ""}'
    )


async def make_email(addresses, invoice, label, missing, booking_state):
    email_body = TEMPLATES.get_template('email_body.html').render(
        {
            'booking_state': booking_state,
            'invoice': invoice,
            'label': label,
            'missing': missing,
        }
    )
    subject_str = await subject(invoice.stem if invoice else None, missing is not False, label is not False)
    email_obj = Email(
        to_address=addresses,
        subject=subject_str,
        body=email_body,
        attachment_paths=[x for x in [label, invoice] if x],
    )
    return email_obj


TEMPLATES = Jinja2Templates(directory=str(am_sett().base_dir / 'front' / 'templates'))


async def get_booking(booking_id: int, session: Session) -> BookingStateDB:
    record = session.get(BookingStateDB, booking_id)
    if not isinstance(record, BookingStateDB):
        raise ValueError(f'No booking found with id {booking_id}')
    return record


def wait_label(shipment_num, dl_path: str, el_client: ELClient) -> pathlib.Path:
    label_path = el_client.get_label(ship_num=shipment_num, dl_path=dl_path).resolve()
    for i in range(20):
        if label_path:
            return label_path
        else:
            print('waiting for file to be created')
            time.sleep(1)
    else:
        raise ValueError(f'file not created after 20 seconds {label_path=}')


async def get_invoice_path(record: AmherstRecord) -> pathlib.Path | None:
    if record.cmc_table_name == 'Customer':
        raise ValueError('invoice not for customer')
    return record.invoice_path


async def get_missing(record: AmherstRecord) -> list[str]:
    if not record.cmc_table_name == 'Hire':
        raise ValueError('missing kit only for hire')
    return record.missing_kit()
