from app.db.mysql import cursor, conn


def filter_campaign_candidates(campaign_id: int):
    """
    Select influencers that satisfy campaign constraints
    and insert them into campaign_candidates
    """

    query = """
    INSERT IGNORE INTO campaign_candidates (campaign_id, influencer_id)
    SELECT
        c.campaign_id,
        i.influencer_id
    FROM campaigns c
    JOIN influencers i ON 1=1
    LEFT JOIN dna_similarity d
        ON d.influencer_id = i.influencer_id
       AND d.campaign_id = c.campaign_id
    WHERE c.campaign_id = %s
      AND i.subscriber_count BETWEEN c.min_subscribers AND c.max_subscribers
      AND (c.target_region IS NULL OR i.region = c.target_region)
      AND (c.required_style IS NULL OR i.category = c.category)
      AND (
            d.similarity_score IS NULL
            OR d.similarity_score >= c.dna_similarity_threshold
          )
    """

    cursor.execute(query, (campaign_id,))
    conn.commit()

    print("✅ Candidate influencers selected")
