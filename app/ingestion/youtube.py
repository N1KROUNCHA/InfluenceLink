from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from app.db.mongo import db

load_dotenv()

youtube = build(
    "youtube",
    "v3",
    developerKey=os.getenv("YOUTUBE_API_KEY")
)

def fetch_channel_data(channel_username):
    request = youtube.channels().list(
        part="snippet,statistics",
        forUsername=channel_username
    )
    response = request.execute()

    if response["items"]:
        db.influencers_full.insert_one(response["items"][0])
        print("Channel data stored in MongoDB")
    else:
        print("No channel found")
