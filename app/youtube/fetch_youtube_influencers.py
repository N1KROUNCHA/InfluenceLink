import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def search_channels(query, max_results=50):
    request = youtube.search().list(
        part="snippet",
        q=query,
        type="channel",
        maxResults=max_results
    )
    return request.execute()["items"]


def get_channel_details(channel_ids):
    request = youtube.channels().list(
        part="snippet,statistics",
        id=",".join(channel_ids)
    )
    return request.execute()["items"]
