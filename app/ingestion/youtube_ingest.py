from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from app.db.mongo import db

load_dotenv()

youtube = build(
    "youtube", "v3",
    developerKey=os.getenv("YOUTUBE_API_KEY")
)

def get_channel_id(query):
    req = youtube.search().list(
        part="snippet",
        q=query,
        type="channel",
        maxResults=1
    )
    res = req.execute()
    return res["items"][0]["snippet"]["channelId"]
def fetch_channel_by_id(channel_id):
    req = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    res = req.execute()

    channel = res["items"][0]
    db.influencers_full.insert_one(channel)
    print("REAL channel data inserted")
