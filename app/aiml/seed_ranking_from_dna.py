from app.db.mysql import cursor, conn

def seed_ranking_from_dna():
    query = """
    INSERT INTO ranking_scores (
        campaign_id,
        influencer_id,
        normalized_score,
        confidence_level
    )
    SELECT
        d.campaign_id,
        d.influencer_id,
        d.similarity_score,
        0.85
    FROM dna_similarity d
    ON DUPLICATE KEY UPDATE
        normalized_score = VALUES(normalized_score),
        confidence_level = VALUES(confidence_level)
    """

    cursor.execute(query)
    conn.commit()

    print("✅ ranking_scores populated from dna_similarity")

if __name__ == "__main__":
    seed_ranking_from_dna()
