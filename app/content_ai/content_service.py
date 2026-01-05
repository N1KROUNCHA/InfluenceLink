from app.content_ai.content_generator1 import generate_content
from app.db.mongo import db
from app.db.mysql import cursor


def generate_campaign_content(campaign_id: int):

    # ---------------- CAMPAIGN ----------------
    cursor.execute("""
        SELECT title, category, target_region, required_style
        FROM campaigns
        WHERE campaign_id = %s
    """, (campaign_id,))
    row = cursor.fetchone()

    if not row:
        raise Exception("Campaign not found")

    brand = {
        "title": row[0],
        "category": row[1],
        "target_region": row[2],
        "required_style": row[3],
    }

    # ---------------- INFLUENCER DNA ----------------
    influencers = list(
        db.influencer_dna.find(
            {},
            {"style": 1, "topics": 1, "_id": 0}
        ).limit(50)
    )

    # ---------------- TRENDS ----------------
    trend_doc = db.trends.find_one({"category": brand["category"]})
    trends = trend_doc.get("keywords", []) if trend_doc else []

    return generate_content(
        brand=brand,
        influencers=influencers,
        trends=trends
    )
