from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")


def youtube_client():
    return build("youtube", "v3", developerKey=API_KEY)


def search_channels(query="fitness", max_results=1000):
    yt = youtube_client()
    channels = []
    next_page = None

    while len(channels) < max_results:
        request = yt.search().list(
            q=query,
            type="channel",
            part="snippet",
            maxResults=50,
            pageToken=next_page
        )

        response = request.execute()

        for item in response.get("items", []):
            channels.append({
                "channel_id": item["snippet"]["channelId"],
                "title": item["snippet"]["title"],
                "description": item["snippet"].get("description", "")
            })

        next_page = response.get("nextPageToken")
        if not next_page:
            break

    return channels
