import os
import sys
import re
from datetime import timedelta
from googleapiclient.discovery import build


class YouTubePlaylistDurationCalculator:
    def __init__(self, api_key, playlist_id, video_range):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)
        self.total_seconds = 0
        self.playlist_id = playlist_id
        self.video_range = video_range
        self.next_page_token = None

    @staticmethod
    def get_duration_seconds(duration):
        hours_match = re.search(r'(\d+)H', duration)
        minutes_match = re.search(r'(\d+)M', duration)
        seconds_match = re.search(r'(\d+)S', duration)

        hours = int(hours_match.group(1)) if hours_match else 0
        minutes = int(minutes_match.group(1)) if minutes_match else 0
        seconds = int(seconds_match.group(1)) if seconds_match else 0

        return timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()

    def fetch_playlist_duration(self):
        video_counter = 0
        while True:
            playlist_items_request = self.youtube.playlistItems().list(
                part='contentDetails',
                playlistId=self.playlist_id,
                maxResults=50,
                pageToken=self.next_page_token
            )

            playlist_items_response = playlist_items_request.execute()
            video_ids = [item['contentDetails']['videoId'] for item in playlist_items_response['items']]

            videos_request = self.youtube.videos().list(
                part="contentDetails",
                id=','.join(video_ids)
            )

            videos_response = videos_request.execute()

            if self.video_range:
                start, end = map(int, self.video_range.split('-'))
                for item in videos_response['items']:
                    video_counter += 1
                    if start <= video_counter <= end:
                        self.total_seconds += self.get_duration_seconds(item['contentDetails']['duration'])
            else:
                for item in videos_response['items']:
                    self.total_seconds += self.get_duration_seconds(item['contentDetails']['duration'])

            self.next_page_token = playlist_items_response.get('nextPageToken')

            if not self.next_page_token:
                break

    def calculate_duration(self):
        self.fetch_playlist_duration()
        total_seconds = int(self.total_seconds)
        minutes, seconds = divmod(total_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        hours = '0' + str(hours) if hours < 10 else hours
        minutes = '0' + str(minutes) if minutes < 10 else minutes
        seconds = '0' + str(seconds) if seconds < 10 else seconds
        return f'{hours}:{minutes}:{seconds}'


def main():
    playlist_id = sys.argv[1]
    api_key = os.environ.get('YT_API_KEY')
    if len(sys.argv) > 2:
        video_range = sys.argv[2]
    else:
        video_range = None

    calculator = YouTubePlaylistDurationCalculator(api_key, playlist_id, video_range)
    result = calculator.calculate_duration()
    print(result)


if __name__ == "__main__":
    main()
