from app.agents.matching_agent.matcher import run_matcher
from app.db.mysql import conn, cursor

def run(campaign_id: int):
    results = run_matcher(campaign_id)

    rank = 1
    for r in results:
        cursor.execute("""
            SELECT influencer_id
            FROM influencers
            WHERE channel_id = %s
        """, (r["channel_id"],))
        inf = cursor.fetchone()

        if not inf:
            continue

        cursor.execute("""
            INSERT INTO ranking_scores (
                campaign_id,
                influencer_id,
                model_version,
                raw_score,
                normalized_score,
                rank_position,
                confidence_level
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                raw_score = VALUES(raw_score),
                normalized_score = VALUES(normalized_score),
                rank_position = VALUES(rank_position)
        """, (
            campaign_id,
            inf[0],
            "v2-dna-matcher",
            r["score"],
            round(r["score"], 4),
            rank,
            min(1.0, r["score"])
        ))

        rank += 1

    conn.commit()
    print("✅ Matching completed & stored")

if __name__ == "__main__":
    run(2)  # change campaign id if needed
