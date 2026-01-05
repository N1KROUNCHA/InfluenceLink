from googleapiclient.discovery import build
from app.config import YOUTUBE_API_KEY

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def discover_channels(keyword, max_results=10):
    request = youtube.search().list(
        q=keyword,
        type="channel",
        part="snippet",
        maxResults=max_results
    )
    response = request.execute()

    channel_ids = []
    for item in response["items"]:
        channel_ids.append(item["snippet"]["channelId"])

    return list(set(channel_ids))
