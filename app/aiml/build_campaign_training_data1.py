from app.db.mysql import cursor, conn
from app.db.mongo import db
from app.aiml.dna_similarity import compute_dna_similarity


def safe(x, default=0.0):
    try:
        return float(x)
    except:
        return default


def topic_overlap(a, b):
    if not a or not b:
        return 0.0
    return len(set(map(str.lower, a)) & set(map(str.lower, b))) / max(len(a), 1)


def build_campaign_training_data(campaign_id: int):
    print("🔧 Building campaign training data...")

    cursor.execute("""
        SELECT category, min_subscribers, max_subscribers,
               target_region, required_style
        FROM campaigns WHERE campaign_id=%s
    """, (campaign_id,))
    row = cursor.fetchone()

    if not row:
        raise Exception("Campaign not found")

    category, min_subs, max_subs, region, style = row

    brand_dna = db.brand_dna.find_one({"campaign_id": campaign_id}) or {}
    brand_embedding = brand_dna.get("embedding", [])
    brand_topics = brand_dna.get("topics", [])

    cursor.execute("""
        SELECT influencer_id, subscriber_count, avg_views,
               engagement_score, authenticity_score,
               category, region, style
        FROM influencers
    """)

    influencers = cursor.fetchall()

    inserted = 0

    for row in influencers:
        influencer_id = row["influencer_id"]
        subs = row["subscriber_count"]
        avg_views = row["avg_views"]
        engagement = row["engagement_score"]
        authenticity = row["authenticity_score"]
        inf_category = row["category"]
        inf_region = row["region"]
        inf_style = row["style"]

        # Mongo DNA (optional)
        dna = db.influencer_dna.find_one({"influencer_id": influencer_id}) or {}

        emb = dna.get("embedding", [])
        topics = dna.get("topics", [])

        dna_sim = compute_dna_similarity(brand_embedding, emb) if emb and brand_embedding else 0.01

        topic_sim = 0.0
        if brand_topics and topics:
            topic_sim = len(set(map(str.lower, brand_topics)) &
                            set(map(str.lower, topics))) / max(len(brand_topics), 1)

        category_match = 1 if inf_category == category else 0
        style_match = 1 if inf_style == style else 0
        region_match = 1 if inf_region == region else 0

        try:
            cursor.execute("""
                INSERT INTO campaign_training_data (
                    campaign_id,
                    influencer_id,
                    subscriber_count,
                    avg_views,
                    engagement_score,
                    authenticity_score,
                    dna_similarity,
                    topic_overlap,
                    category_match,
                    style_match,
                    region_match
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    subscriber_count=VALUES(subscriber_count),
                    avg_views=VALUES(avg_views),
                    engagement_score=VALUES(engagement_score),
                    authenticity_score=VALUES(authenticity_score),
                    dna_similarity=VALUES(dna_similarity),
                    topic_overlap=VALUES(topic_overlap),
                    category_match=VALUES(category_match),
                    style_match=VALUES(style_match),
                    region_match=VALUES(region_match)
            """, (
                campaign_id,
                influencer_id,
                safe(subs),
                safe(avg_views),
                safe(engagement),
                safe(authenticity),
                safe(dna_sim),
                safe(topic_sim),
                category_match,
                style_match,
                region_match
            ))

            inserted += 1

        except Exception as e:
            print("⚠️ Skip influencer", influencer_id, "→", e)

    conn.commit()
    print(f"✅ Inserted {inserted} training rows")

