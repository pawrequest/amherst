import webbrowser
import argparse

RM_URL = 'https://www.royalmail.com/track-your-item#/tracking-results/'


def convert_parcelforce_tracking_to_royal_mail(old_track_url: str) -> str:
    print(f'Converting Parcelforce tracking URL: {old_track_url}')
    track_num = old_track_url.split('=')[1]
    track_num = f'PB{track_num}'
    track_num = f'{track_num}001'
    new_track_url = f'{RM_URL}{track_num}'
    print(new_track_url)
    return new_track_url


if __name__ == '__main__':
    url = 'https://www.parcelforce.com/track-trace?trackNumber=UK3467769'
    convert_parcelforce_tracking_to_royal_mail(url)
