from googleapiclient.discovery import build
from dotenv import load_dotenv
import os

load_dotenv()

youtube = build(
    "youtube", "v3",
    developerKey=os.getenv("YOUTUBE_API_KEY")
)

def discover_channels(keyword, max_results=5):
    req = youtube.search().list(
        part="snippet",
        q=keyword,
        type="channel",
        maxResults=max_results
    )
    res = req.execute()

    return [item["snippet"]["channelId"] for item in res["items"]]
