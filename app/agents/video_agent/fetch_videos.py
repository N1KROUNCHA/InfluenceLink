from googleapiclient.discovery import build
from app.config import YOUTUBE_API_KEY
from app.db.mongo import db

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def fetch_recent_videos(channel_id, max_results=10):
    req = youtube.search().list(
        part="snippet",
        channelId=channel_id,
        order="date",
        maxResults=max_results,
        type="video"
    )
    res = req.execute()

    videos = []
    for item in res.get("items", []):
        snippet = item["snippet"]

        videos.append({
            "video_id": item["id"]["videoId"],
            "channel_id": channel_id,
            "title": snippet["title"],
            "description": snippet["description"],
            "publishedAt": snippet["publishedAt"]
        })

    return videos
