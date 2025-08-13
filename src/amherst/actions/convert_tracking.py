import webbrowser
import argparse

RM_URL = 'https://www.royalmail.com/track-your-item#/tracking-results/'


def convert_parcelforce_tracking_to_royal_mail(old_track_url: str):
    track_num = old_track_url.split('=')[1]
    track_num = f'PB{track_num}001'
    track_num = f'{RM_URL}{track_num}'
    print(track_num)
    webbrowser.open(track_num, new=2)


