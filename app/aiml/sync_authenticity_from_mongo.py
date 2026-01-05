from app.db.mongo import db
from app.db.mysql import cursor, conn

def sync_authenticity():
    docs = db.influencer_dna.find(
        {"authenticity_score": {"$exists": True}}
    )

    updated = 0

    for doc in docs:
        channel_id = doc.get("channel_id")
        auth = doc.get("authenticity_score")

        if channel_id is None:
            continue

        cursor.execute("""
            UPDATE influencers
            SET authenticity_score = %s
            WHERE channel_id = %s
        """, (auth, channel_id))

        if cursor.rowcount > 0:
            updated += 1

    conn.commit()
    print(f"✅ Synced authenticity for {updated} influencers")


if __name__ == "__main__":
    sync_authenticity()
