from __future__ import annotations

import time
import typing as _t
import pathlib

from shipaw import ELClient
from sqlmodel import Session
from starlette.templating import Jinja2Templates
from suppawt.office_ps.email_handler import Email
import shipaw
from pycommence import PyCommence
from shipaw.models import pf_msg
from shipaw.models.pf_shipment import ShipmentRequest
from loguru import logger

from amherst.am_config import am_sett
from amherst.am_shared import HireFields
from amherst.models.am_record import AmherstRecord
from amherst.models.db_models import BookingStateDB

type EmailChoices = _t.Literal['invoice', 'label', 'missing_kit']


def book_shipment(el_client, shipment_request: ShipmentRequest) -> pf_msg.CreateShipmentResponse:
    resp = el_client.send_shipment_request(shipment_request)
    for a in resp.alerts if resp.alerts else []:
        if a.type == 'ERROR':
            logger.error(f'ERROR IN BOOKING: {a.message}')
            raise shipaw.ExpressLinkError(a.message)
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

    except Exception as exce:
        logger.error(f'Failed to record tracking for {record.name} due to:\n{exce}')


def do_record_tracking(booking: BookingStateDB):
    direction = booking.direction
    tracking_number = booking.response.shipment_num
    category = booking.record.cmc_table_name
    record_name = booking.record.name
    tracking_link_field = HireFields.TRACK_INBOUND if direction in ['in', 'dropoff'] \
        else HireFields.TRACK_OUTBOUND
    tracking_link = booking.response.tracking_link()

    with PyCommence.from_table_name_context(table_name=category) as py_cmc:
        py_cmc.edit_record(
            record_name,
            row_dict={
                tracking_link_field: tracking_link,
                HireFields.DB_LABEL_PRINTED: True
            },
        )
        booking.tracking_logged = True
    logger.info(
        f'Set DB Printed and Updated "{record_name}" {tracking_link_field} to {tracking_link}'
    )


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
    subject_str = await subject(
        invoice.stem if invoice else None,
        missing is not False,
        label is not False
    )
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
    completed_dl_path = el_client.get_label(ship_num=shipment_num, dl_path=dl_path).resolve()
    for i in range(20):
        if completed_dl_path:
            return completed_dl_path
        else:
            print('waiting for file to be created')
            time.sleep(1)
    else:
        raise ValueError(f'file not created after 20 seconds {completed_dl_path=}')


async def get_invoice_path(record: AmherstRecord) -> pathlib.Path | None:
    if record.cmc_table_name == 'Customer':
        raise ValueError('invoice not for customer')
    return record.invoice_path


async def get_missing(record: AmherstRecord) -> list[str]:
    if not record.cmc_table_name == 'Hire':
        raise ValueError('missing kit only for hire')
    return record.missing_kit()
