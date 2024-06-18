from shipaw.expresslink_client import ELClient
from shipaw.pf_config import PFSettings


def expresslink_live():
    el_client = ELClient(
        settings=PFSettings(
            _env_file=r'R:\paul_r\.internal\envs\pf_live.env',
        ),
    )
    return el_client


def get_a_label(dl_path, shipment_number):
    # el_client = expresslink_live()
    el_client = ELClient()
    return el_client.get_label(shipment_number, dl_path)


def get_manifest():
    # el_client = expresslink_live()
    el_client = ELClient()
    sdggd = el_client.get_manifest()
    ...


if __name__ == '__main__':
    print(get_manifest())

    # myfile = get_a_label('got_a_label.pdf', 'ER9463748 ')
    # os.startfile(myfile)

    # pawdf.array_pdf.convert_many(myfile, print_files=True)

    ...
