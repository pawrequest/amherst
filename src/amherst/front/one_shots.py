import pawdf
from shipaw import ELClient
from shipaw.pf_config import PFSettings


def expresslink_live():
    el_client = ELClient(
        settings=PFSettings(
            _env_file=r'R:\paul_r\.internal\envs\pf_live.env',
        ),
    )
    return el_client


def get_a_label(dl_path, shipment_number):
    el_client = expresslink_live()
    return el_client.get_label(shipment_number, dl_path)


if __name__ == '__main__':
    # myfile = (get_a_label('got_a_label.pdf', 'ML8598580'))
    # pawdf.array_pdf.convert_many(myfile, print_files=True)

    ...
