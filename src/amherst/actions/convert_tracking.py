import webbrowser
import argparse

RM_URL = 'https://www.royalmail.com/track-your-item#/tracking-results/'


def convert_parcelforce_tracking_to_royal_mail(old_track_url: str):
    print(f'Converting Parcelforce tracking URL: {old_track_url}')
    # if not old_track_url[1].lower() == 'b':
    #     raise ValueError('No "B" in string pos 2 - is this a tracking number?')
    track_num = old_track_url.split('=')[1]
    track_num = f'{track_num}001'
    track_num = f'{RM_URL}{track_num}'
    print(track_num)
    webbrowser.open(track_num, new=2)


