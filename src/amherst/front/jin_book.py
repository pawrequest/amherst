from loguru import logger

import shipaw
from amherst.am_shared import HireFields
from amherst.models.shipment_record import ShipmentRecordInDB
from pycommence import PyCommence
from shipaw import BookingState, ELClient
from shipaw.models.all_shipment_types import ShipmentRequest


def process_shipment_request(shipment_request: ShipmentRequest, el_client: ELClient):
    """Process the shipment.

    Update the shiprec with the booking shipment and wait for the label to download.
    Open the label file in OS default pdf handler.

    Args:
        shipment_request (shipment_record.ShipmentRecordDB): The shiprec object.
        el_client (ELClient): :class:`~ELClient` object.

    Returns:
        shiprecs.ShipmentRecordDB: The shiprec object.

    Raises:
        shipaw.ExpressLinkError: If the shipment is not completed.

    """
    return shipment_request


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
