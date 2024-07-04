from __future__ import annotations

import typing as _t

from fastapi import Depends, Path
from sqlmodel import SQLModel, Session
from starlette.templating import Jinja2Templates
from suppawt.office_ps.email_handler import Email

from amherst.config import settings
from amherst.db import get_session, model_type_from_path
from amherst.models.am_record_smpl import AMHERST_TABLE_TYPES

# from amherst.models.db_models import BookingStateDB

type EmailChoices = _t.Literal['invoice', 'label', 'missing_kit']


# def record_tracking(booking_state: BookingStateDB):
#     record = booking_state.record
#     try:
#         category = record.category
#         if category == 'Customer':
#             logger.error('CANT LOG TO CUSTOMER')
#             return
#         do_record_tracking(booking_state)
#         logger.debug(f'Logged tracking for {category} {record.name}')
#
#     except Exception as exce:
#         logger.exception(exce)
#         raise


# def do_record_tracking(booking: BookingStateDB):
#     tracking_link = booking.response.tracking_link()
#     cmc_package = (
#         {
#             HireAliases.TRACK_INBOUND: tracking_link,
#             HireAliases.ARRANGED_INBOUND: True,
#             HireAliases.PICKUP_DATE: f'{booking.shipment_request.shipping_date:%Y-%m-%d}',
#         }
#         if booking.direction in ['in', 'dropoff']
#         else {HireAliases.TRACK_OUTBOUND: tracking_link, HireAliases.ARRANGED_OUTBOUND: True}
#     )
#
#     with PyCommence.with_csr(csrname=booking.record.category) as py_cmc:
#         py_cmc.edit_record(booking.record.name, row_dict=cmc_package)
#     booking.tracking_logged = True
#     logger.debug(f'Logged {str(cmc_package)} to Commence')


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


TEMPLATES = Jinja2Templates(directory=str(settings().base_dir / 'front' / 'templates'))


async def new_amrec_f_path(
        row_id: str = Path(),
        category: type[SQLModel] = Depends(model_type_from_path),
        session: Session = Depends(get_session)
) -> AMHERST_TABLE_TYPES:
    ret = session.get(category, id)
    if not isinstance(ret, category):
        raise ValueError(f'No record found with id {row_id}')
    return ret


async def amrec_from_path(
        row_id: str = Path(),
        category: type[SQLModel] = Depends(model_type_from_path),
        session: Session = Depends(get_session)
):
    return session.get(category, row_id)
