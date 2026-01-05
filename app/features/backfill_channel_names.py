from app.db.mongo import db
from app.db.mysql import cursor, conn

def backfill_channel_names():
    mongo_channels = db.influencers_full.find(
        {"snippet.title": {"$exists": True}},
        {"snippet.title": 1, "id": 1}
    )

    updated = 0

    for ch in mongo_channels:
        channel_id = ch.get("id")
        channel_name = ch["snippet"]["title"]

        if channel_id and channel_name:
            cursor.execute("""
                UPDATE influencers
                SET channel_name = %s
                WHERE channel_id = %s
            """, (channel_name, channel_id))
            updated += 1

    conn.commit()
    print(f"Backfilled channel names for {updated} influencers")

if __name__ == "__main__":
    backfill_channel_names()
