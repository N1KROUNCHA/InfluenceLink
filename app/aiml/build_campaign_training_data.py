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
    a = set(map(str.lower, a))
    b = set(map(str.lower, b))
    return len(a & b) / max(len(a), 1)


def build_campaign_training_data(campaign_id: int):
    print("🔧 Building campaign training data (prefiltered)...")

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
        WHERE subscriber_count BETWEEN %s AND %s
    """, (min_subs, max_subs))

    influencers = cursor.fetchall()

    scored = []

    for row in influencers:
        (
            influencer_id,
            subs,
            avg_views,
            engagement,
            authenticity,
            inf_category,
            inf_region,
            inf_style
        ) = row

        dna = db.influencer_dna.find_one({"influencer_id": influencer_id})
        if not dna:
            continue

        emb = dna.get("embedding", [])
        topics = dna.get("topics", [])

        dna_sim = compute_dna_similarity(brand_embedding, emb) if emb else 0.0
        topic_sim = topic_overlap(brand_topics, topics)

        # 🔥 PREFILTER LOGIC (very important)
        if dna_sim < 0.20 and topic_sim < 0.10:
            continue

        scored.append((
            influencer_id,
            subs,
            avg_views,
            engagement,
            authenticity,
            inf_category,
            inf_region,
            inf_style,
            dna_sim,
            topic_sim
        ))

    # keep top 150 by semantic strength
    scored = sorted(scored, key=lambda x: (x[8], x[9]), reverse=True)[:150]

    inserted = 0

    for row in scored:
        (
            influencer_id,
            subs,
            avg_views,
            engagement,
            authenticity,
            inf_category,
            inf_region,
            inf_style,
            dna_sim,
            topic_sim
        ) = row

        category_match = 1 if inf_category == category else 0
        style_match = 1 if inf_style == style else 0
        region_match = 1 if inf_region == region else 0

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
            dna_sim,
            topic_sim,
            category_match,
            style_match,
            region_match
        ))

        inserted += 1

    conn.commit()
    print(f"✅ campaign_training_data rows inserted: {inserted}")
