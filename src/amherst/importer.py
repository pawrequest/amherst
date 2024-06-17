from __future__ import annotations

from loguru import logger

from amherst.models import db_models
from amherst.models.am_record import AmherstRecord, AmherstRecordIn
from shipaw.expresslink_client import ELClient
from shipaw.models.pf_models import AddressTemporary
from shipaw.models.pf_msg import Alert, Alerts
from shipaw.models.pf_shipment import ShipmentRequest
from shipaw.ship_types import AlertType, ShipmentType


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
        chosen_address, score = el_client.choose_address(record.input_address)
        altyp = AlertType.NOTIFICATION if score > 80 else AlertType.WARNING if score > 60 else AlertType.ERROR
        record.alerts.alert.append(Alert(message=f'address score {score}', type=altyp))
        return ShipmentRequest(
            recipient_contact=record.contact(),
            recipient_address=chosen_address,
            shipping_date=record.send_date,
            total_number_of_parcels=record.boxes,
            **ref_nums,
            shipment_type=ShipmentType.DELIVERY
        )
    except Exception as e:
        logger.exception(e)
        raise

        # chosen_address = AddressTemporary.model_validate(
        #     record.input_address,
        #     from_attributes=True
        # )
        # record.alerts.alert.append(Alert(message='Using Incomplete Address Data'))


async def amrec_to_booking(amrec):
    booking = db_models.BookingStateDB(
        record=amrec,
        shipment_request=(amherst_shipment_request(amrec)),
        # alerts=Alerts(alert=[Alert(code=None, message='Created')])
    )
    return booking


async def cmc_record_to_amrec(record):
    amrec_in = AmherstRecordIn(**record)
    amrec_in = amrec_in.model_validate(amrec_in)
    amrec = AmherstRecord(**amrec_in.model_dump())
    return amrec
