from __future__ import annotations

import typing as _t

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


