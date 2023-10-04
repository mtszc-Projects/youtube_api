import os
import re
from datetime import timedelta
from googleapiclient.discovery import build


def get_duration_seconds(duration):
    hours_match = re.search(r'(\d+)H', duration)
    minutes_match = re.search(r'(\d+)M', duration)
    seconds_match = re.search(r'(\d+)S', duration)

    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0
    seconds = int(seconds_match.group(1)) if seconds_match else 0

    return timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()


def main():
    api_key = os.environ.get('YT_API_KEY')

    youtube = build('youtube', 'v3', developerKey=api_key)

    total_seconds = 0
    playlist_id = 'PLHtUOYOPwzJGGZkjR-FspIL17YtSBGaCR'
    next_page_token = None

    while True:
        playlist_items_request = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )

        playlist_items_response = playlist_items_request.execute()
        video_ids = [item['contentDetails']['videoId'] for item in playlist_items_response['items']]

        videos_request = youtube.videos().list(
            part="contentDetails",
            id=','.join(video_ids)
        )

        videos_response = videos_request.execute()

        for item in videos_response['items']:
            total_seconds += get_duration_seconds(item['contentDetails']['duration'])

        next_page_token = playlist_items_response.get('next_page_token')

        if not next_page_token:
            break

    total_seconds = int(total_seconds)
    minutes, seconds = divmod(total_seconds, 60)
    hours, minutes = divmod(minutes, 60)

    print(f'{hours}:{minutes}:{seconds}')


if __name__ == "__main__":
    main()
