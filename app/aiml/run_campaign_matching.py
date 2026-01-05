from app.db.mongo import db
from app.db.mysql import cursor, conn
from app.aiml.dna_similarity1 import compute_dna_similarity


def run_campaign_matching(campaign_id: int):
    brand = db.brand_dna.find_one({"campaign_id": campaign_id})
    if not brand:
        print("❌ Brand DNA missing")
        return

    influencers = list(db.influencer_dna.find())
    print(f"🔍 Matching {len(influencers)} influencers")

    for infl in influencers:
        channel_id = infl.get("channel_id")

        cursor.execute(
            "SELECT influencer_id FROM influencers WHERE channel_id=%s",
            (channel_id,)
        )
        row = cursor.fetchone()
        if not row:
            continue

        influencer_id = row[0]

        similarity = compute_dna_similarity(
            brand["embedding"],
            infl["embedding"]
        )

        cursor.execute("""
            INSERT INTO dna_similarity (campaign_id, influencer_id, similarity_score)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE similarity_score = VALUES(similarity_score)
        """, (campaign_id, influencer_id, similarity))

    conn.commit()
    print("✅ DNA similarity generated")


if __name__ == "__main__":
    run_campaign_matching(2)
