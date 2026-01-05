from app.db.mongo import db
from app.db.mysql import cursor, conn

def sync_influencer_metadata():
    docs = db.influencer_dna.find()

    updated = 0
    for doc in docs:
        channel_id = doc.get("channel_id")
        if not channel_id:
            continue

        style = doc.get("style")
        authenticity = doc.get("authenticity_score", 0.5)

        cursor.execute("""
            UPDATE influencers
            SET
                style = %s,
                authenticity_score = %s
            WHERE channel_id = %s
        """, (style, authenticity, channel_id))

        updated += 1

    conn.commit()
    print(f"✅ Synced metadata for {updated} influencers")


if __name__ == "__main__":
    sync_influencer_metadata()
