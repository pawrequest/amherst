from __future__ import annotations, annotations

import time
import typing as _t
import pathlib

from sqlmodel import Session
from starlette.templating import Jinja2Templates

from amherst.am_config import am_sett
from amherst.models.db_models import BookingStateDB
from shipaw import ELClient
from amherst.models.am_record import AmherstRecord

type EmailChoices = _t.Literal['invoice', 'label', 'missing_kit']

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
