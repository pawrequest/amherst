# /// script
# requires-python = ">=3.13"
# dependencies = [
#   "pycommence==0.2.4",
# ]
# ///
import sys
from functools import partial
from typing import TYPE_CHECKING

from pycommence import MoreAvailable, pycommence_context
from pycommence.filters import ConditionType, FieldFilter, FilterArray

if TYPE_CHECKING:
    from amherst.models.commence_shipment import ShipmentStatus


def toggle_shipment_status(barcode: str, status: 'ShipmentStatus'):
    fil = FieldFilter(column='Latest Tracking', value=barcode, condition=ConditionType.CONTAIN)
    fa = FilterArray.from_filters(fil)
    with pycommence_context('Shipment') as p:
        matching_shipments = list(p.read_rows(filter_array=fa))
        if len(matching_shipments) > 1:
            raise ValueError('Multiple Shipments found')
        if isinstance(matching_shipments, MoreAvailable):
            raise TypeError('MoreAvailable instance encountered')
        row_id = matching_shipments[0].row_info.id
        updater = {'Status': status}
        p.update_row(row_id=row_id, update_pkg=updater)
    print(f'Updated: {updater}')


set_shipment_sent = partial(toggle_shipment_status, status='Sent')
set_shipment_received = partial(toggle_shipment_status, status='Received')


def get_related(barcode: str):
    fil = FieldFilter(column='Latest Tracking', value=barcode, condition=ConditionType.CONTAIN)
    fa = FilterArray.from_filters(fil)
    with pycommence_context('Shipment') as p:
        res = p.read_rows(filter_array=fa)
    # return list(res)
    results = []
    for info, data in res:
        customer = data.get('For Customer')
        hire = data.get('For Hire')
        sale = data.get('For Sale')
        results.append({'customer': customer, 'hire': hire, 'sale': sale})

    return results


if __name__ == '__main__':
    try:
        mode = input('Choose mode - [s]send or [r]eceive: ')
        if mode.lower() == 's':
            f = set_shipment_sent
        elif mode.lower() == 'r':
            f = set_shipment_received
        else:
            raise ValueError('Invalid mode selected')
        user = 1
        while user:
            user = input('Scan a Barcode: (enter to quit)')
            if user and isinstance(user, str):
                f(user)
            else:
                user = None
    finally:
        input('Enter to Close')
        sys.exit()
