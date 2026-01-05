from app.db.mysql import cursor, conn

def generate_reason(row):
    reasons = []

    if row["dna_similarity"] >= 0.35:
        reasons.append("high content DNA similarity")

    if row["engagement_score"] and row["engagement_score"] > 0.05:
        reasons.append("strong audience engagement")

    if row["authenticity_score"] and row["authenticity_score"] > 0.5:
        reasons.append("authentic engagement behavior")

    if row["category_match"] == 1:
        reasons.append("matches campaign category")

    if row["style_match"] == 1:
        reasons.append("matches brand style")

    if row["region_match"] == 1:
        reasons.append("matches target region")

    if not reasons:
        return "Selected based on overall AI ranking score"

    return "Recommended because of " + ", ".join(reasons)


def build_explanations():
    cursor.execute("""
        SELECT
            campaign_id,
            influencer_id,
            dna_similarity,
            engagement_score,
            authenticity_score,
            category_match,
            style_match,
            region_match
        FROM campaign_training_data
    """)

    rows = cursor.fetchall()

    if not rows:
        print("❌ No rows found for explanation generation")
        return

    for row in rows:
        explanation = generate_reason({
            "dna_similarity": row[2],
            "engagement_score": row[3],
            "authenticity_score": row[4],
            "category_match": row[5],
            "style_match": row[6],
            "region_match": row[7],
        })

        cursor.execute("""
            INSERT INTO ranking_explanations
            (campaign_id, influencer_id, explanation)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE explanation = VALUES(explanation)
        """, (
            row[0],
            row[1],
            explanation
        ))

    conn.commit()
    print("✅ Ranking explanations generated successfully")


if __name__ == "__main__":
    build_explanations()
