from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")


def youtube_client():
    return build("youtube", "v3", developerKey=API_KEY)


def fetch_channel_stats(channel_ids):
    yt = youtube_client()
    results = []

    for i in range(0, len(channel_ids), 50):
        batch = channel_ids[i:i+50]

        res = yt.channels().list(
            part="snippet,statistics",
            id=",".join(batch)
        ).execute()

        for ch in res.get("items", []):
            snippet = ch["snippet"]
            stats = ch["statistics"]

            results.append({
                "channel_id": ch["id"],
                "channel_name": snippet.get("title"),
                "category": snippet.get("categoryId"),
                "region": snippet.get("country"),
                "language": snippet.get("defaultLanguage"),
                "subscriber_count": int(stats.get("subscriberCount", 0)),
                "video_count": int(stats.get("videoCount", 0)),
                "view_count": int(stats.get("viewCount", 0)),
            })

    return results
