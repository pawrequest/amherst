from pathlib import Path

from amherst_core.consts_enums import CategoryName
from shipaw.config import SHIPAW_SETTINGS, populate_providers
from shipaw.nicegui_ui.app import build_shipper, ui

from amherst.amherst_pycmc import row_from_pycommence_sync
from amherst.callbacks import cmc_callback_nice
from amherst.shipment_builders import PycommenceShipment, build_shipment


def get_shipment(category, pk) -> PycommenceShipment:
    row = row_from_pycommence_sync(category=category, record_name=pk)
    record = row.construct_model()
    shipment = build_shipment(record)
    return shipment


def nice_shipper(category, pk, host='127.0.0.1', port=9080):
    populate_providers(SHIPAW_SETTINGS)
    shipment = get_shipment(category, pk)

    @ui.page('/')
    def index():
        on_booking_callback = cmc_callback_nice
        build_shipper(initial=shipment, on_booking=on_booking_callback)

    # storage_path = Path.home() / 'shipaw' / 'nicegui_storage'
    # storage_path.mkdir(parents=True, exist_ok=True)
    # os.environ['NICEGUI_STORAGE_PATH'] = str(storage_path)

    ui.run(
        host=host,
        port=port,
        title='Shipaw Shipper',
        reload=False,
        window_size=(1200, 1000),  # implies native=True
        favicon=Path(r'C:\prdev\amdev\shipaw\src\shipaw\nicegui_ui\favicon.ico'),
        # frameless=True  # todo: close button
        # storage_secret='shipaw-secret',  # if needed
    )


# if __name__ == '__mp_main__':
# if __name__ == '__main__':
#     cat = CategoryName.Customer
#     pkay = 'Test'
#     nice_shipper(cat, pkay)
# main2()
#
#
if __name__ in {'__main__', '__mp_main__'}:
    cat = CategoryName.Customer
    pkay = 'Test'
    if __name__ == '__main__':
        nice_shipper(cat, pkay)
    # main2()
