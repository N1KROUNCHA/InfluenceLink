from app.db.mysql import cursor, conn
from app.db.mongo import db


def enrich_campaign_features():
    """
    Fill missing feature columns so ranking & explanations work for ALL campaigns
    """

    cursor.execute("""
        SELECT DISTINCT campaign_id
        FROM campaign_training_data
    """)
    campaigns = [row[0] for row in cursor.fetchall()]

    for campaign_id in campaigns:
        print(f"🔧 Enriching campaign {campaign_id}")

        cursor.execute("""
            SELECT influencer_id
            FROM campaign_training_data
            WHERE campaign_id = %s
        """, (campaign_id,))

        influencer_ids = [r[0] for r in cursor.fetchall()]

        for influencer_id in influencer_ids:
            # --- Fetch DNA from Mongo ---
            dna = db.influencer_dna.find_one({"influencer_id": influencer_id})

            authenticity = None
            style_match = None

            if dna:
                authenticity = dna.get("authenticity_score", 0.5)
                style_match = 1 if dna.get("style") else 0

            # Default values (safe ML-friendly)
            cursor.execute("""
                UPDATE campaign_training_data
                SET
                    authenticity_score = COALESCE(authenticity_score, %s),
                    style_match = COALESCE(style_match, %s),
                    category_match = COALESCE(category_match, 1),
                    region_match = COALESCE(region_match, 1)
                WHERE campaign_id = %s
                  AND influencer_id = %s
            """, (
                authenticity,
                style_match,
                campaign_id,
                influencer_id
            ))

    conn.commit()
    print("✅ Campaign feature enrichment completed")


if __name__ == "__main__":
    enrich_campaign_features()
