from shipaw.expresslink_client import ELClient
from shipaw.pf_config import PFSettings
from zeep.plugins import HistoryPlugin
from lxml import etree

def expresslink_live():
    el_client = ELClient(
        settings=PFSettings(
            _env_file=r'R:\paul_r\.internal\envs\pf_live.env',
        ),
    )
    return el_client


# el_client = expresslink_live()
el_client = ELClient()


def get_a_label(dl_path, shipment_number):
    return el_client.get_label(shipment_number, dl_path)


if __name__ == '__main__':
    try:
        print(el_client.get_candidates('BS2 0PZ'))
    except Exception as e:
        print(e)
        raise
