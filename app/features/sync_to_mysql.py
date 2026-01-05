from app.db.mongo import db
from app.db.mysql import cursor, conn

def sync_features():
    for doc in db.features.find():
        f = doc["features"]

        cursor.execute("""
            INSERT INTO influencers
            (channel_id, subscriber_count, video_count, engagement_score, avg_views)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
            subscriber_count=%s,
            video_count=%s,
            engagement_score=%s,
            avg_views=%s
        """, (
            doc["channel_id"],
            f["subscriber_count"],
            f["video_count"],
            f["engagement_score"],
            f["avg_views"],
            f["subscriber_count"],
            f["video_count"],
            f["engagement_score"],
            f["avg_views"]
        ))

    conn.commit()
    print("Features synced to MySQL")

if __name__ == "__main__":
    sync_features()
