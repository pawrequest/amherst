import webbrowser
import argparse

RM_URL = 'https://www.royalmail.com/track-your-item#/tracking-results/'


def convert_parcelforce_tracking_to_royal_mail(old_track_url: str):
    print(f'Converting Parcelforce tracking URL: {old_track_url}')
    # if not old_track_url[1].lower() == 'b':
    #     raise ValueError('No "B" in string pos 2 - is this a tracking number?')
    track_num = old_track_url.split('=')[1]
    # if track_num[0:2].lower() in ['zo', 'sp']:
    track_num = f'PB{track_num}'
    track_num = f'{track_num}001'

    new_track_url = f'{RM_URL}{track_num}'
    print(new_track_url)

    webbrowser.open(new_track_url, new=2)

if __name__ == '__main__':
    url = 'https://www.parcelforce.com/track-trace?trackNumber=UK3467769'
    convert_parcelforce_tracking_to_royal_mail(url)
