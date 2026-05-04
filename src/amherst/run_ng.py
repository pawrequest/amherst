from loguru import logger
from pycommence import PyCommence
from shipaw.config import SHIPAW_SETTINGS, populate_providers
from shipaw.nicegui_ui.app import ship_form, ui

from amherst.models.meta import TABLE_REGISTER


def main(host: str = '127.0.0.1', port: int = 9080) -> None:
    """Initialise providers and start the NiceGUI server."""
    from pawlogger import configure_loguru

    configure_loguru(logger, log_file=SHIPAW_SETTINGS.log_file, level=SHIPAW_SETTINGS.log_level)
    populate_providers(SHIPAW_SETTINGS)
    ui.run(
        host=host,
        port=port,
        title='Shipaw Shipper',
        favicon='🚢',
        reload=False,
        native=True,
        window_size=(1200, 900),
    )


def main2():
    category = 'Customer'
    pk = 'Test'
    with PyCommence(category) as pyc:
        row = pyc.item_read_csr(pk=pk)
    record = row.construct_model()
    shipment = record.shipment()
    ship_form(shipment=shipment)


if __name__ in {'__main__', '__mp_main__'}:
    main2()
