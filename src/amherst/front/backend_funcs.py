from __future__ import annotations

from loguru import logger
from suppawt.office_ps.email_handler import Email

import shipaw
from amherst.am_shared import HireFields
from amherst.front.support import TEMPLATES
from amherst.models.shipment_record import ShipmentRecordInDB
from pycommence import PyCommence
from shipaw import BookingState
from shipaw.models.pf_shipment import ShipmentRequest


def book_shipment(el_client, shipment_request: ShipmentRequest) -> BookingState:
    resp = el_client.send_shipment_request(shipment_request)
    for a in resp.alerts if resp.alerts else []:
        if a.type == 'ERROR':
            logger.error(f'ERROR IN BOOKING: {a.message}')
            raise shipaw.ExpressLinkError(a.message)
        logger.warning(f'WARNING IN BOOKING: {a.message}')
    return BookingState(requested_shipment=shipment_request, response=resp, booked=True)


def record_tracking(shiprec: ShipmentRecordInDB):
    try:
        tracking_number = shiprec.booking_state.response.shipment_num
        category = shiprec.record.cmc_table_name
        if category == 'Customer':
            logger.error('CANT LOG TO CUSTOMER')
            return
        record_name = shiprec.record.name
        direction = shiprec.shipment.direction
        do_record_tracking(category, direction, record_name, tracking_number)

    except Exception as exce:
        logger.error(f'Failed to record tracking for {shiprec.record.name} due to:\n{exce}')


def do_record_tracking(category, direction, record_name, tracking_number):
    tracking_link_field = HireFields.TRACK_INBOUND if direction in ['in',
                                                                    'dropoff'] else HireFields.TRACK_OUTBOUND
    pf_url = 'https://www.parcelforce.com/track-trace?trackNumber='
    tracking_link = pf_url + tracking_number

    with PyCommence.from_table_name_context(table_name=category) as py_cmc:
        py_cmc.edit_record(
            record_name,
            row_dict={
                tracking_link_field: tracking_link,
                HireFields.DB_LABEL_PRINTED: True
            },
        )
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
    email_body = TEMPLATES.get_template('email.html').render(
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
