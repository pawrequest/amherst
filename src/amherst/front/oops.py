from shipaw import ELClient
from shipaw.pf_config import PFSettings


def get_a_label(dl_path, shipment_number):
    el_client = expresslink_live()
    return el_client.get_label(shipment_number, dl_path)


def expresslink_live():
    el_client = ELClient(
        settings=PFSettings(
            _env_file=r'R:\paul_r\.internal\envs\pf_live.env',
        ),
    )
    return el_client


if __name__ == '__main__':
    # os.startfile(get_a_label('got_a_label.pdf', 'ML7327665'))
    ...
