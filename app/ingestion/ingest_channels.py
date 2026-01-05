from googleapiclient.discovery import build
from app.config import YOUTUBE_API_KEY
from app.db.mongo import db
from app.db.mysql import cursor, conn

youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

def ingest_channel(channel_id):
    request = youtube.channels().list(
        part="snippet,statistics",
        id=channel_id
    )
    response = request.execute()

    if not response["items"]:
        return

    channel = response["items"][0]

    # Store raw data in MongoDB
    db.influencers_full.insert_one(channel)

    stats = channel["statistics"]
    snippet = channel["snippet"]

    # Insert into MySQL influencers table
    cursor.execute("""
    INSERT IGNORE INTO influencers
    (channel_id, channel_name, subscriber_count, video_count)
    VALUES (%s, %s, %s, %s)
""", (
    channel_id,
    snippet.get("title"),
    int(stats.get("subscriberCount", 0)),
    int(stats.get("videoCount", 0))
))


    conn.commit()
