import os
import pandas as pd
import joblib
from app.db.mysql import conn, cursor

MODEL_PATH = "models/campaign_rank_model.pkl"

FEATURES = [
    "subscriber_count",
    "avg_views",
    "engagement_score",
    "authenticity_score",
    "dna_similarity",
    "topic_overlap",
    "category_match",
    "style_match",
    "region_match"
]


def predict_campaign_ranking(campaign_id: int):
    df = pd.read_sql(
        """
        SELECT *
        FROM campaign_training_data
        WHERE campaign_id = %s
          AND influencer_id IS NOT NULL
        """,
        conn,
        params=(campaign_id,)
    )

    if df.empty or not os.path.exists(MODEL_PATH):
        print("⚠️ Cold Start: Using Vector Similarity for Initial Recommendations")
        
        # fallback: use vector search
        from app.db.mongo import db
        from app.aiml.faiss_search import search_similar
        
        # Get campaign DNA
        campaign_dna = db.campaign_dna.find_one({"campaign_id": campaign_id})
        if not campaign_dna or "embedding" not in campaign_dna:
            print("⚠️ No campaign DNA found")
            return []
            
        # Find similar influencers (fetch more candidates to allow for filtering)
        similar_influencers = search_similar(campaign_dna["embedding"], top_k=500)
        
        # Get campaign category for filtering
        campaign_category = campaign_dna.get("topics", [""])[0] if campaign_dna.get("topics") else ""
        if not campaign_category:
             # Fallback to fetching from DB if not in DNA
             cursor.execute("SELECT category FROM campaigns WHERE campaign_id = %s", (campaign_id,))
             row = cursor.fetchone()
             if row:
                 campaign_category = row["category"]

        results = []
        filtered_count = 0
        
        for i, inf in enumerate(similar_influencers):
            influencer_id = inf["influencer_id"]
             # 🔐 SAFETY CHECK & Category Filter
            cursor.execute(
                "SELECT category FROM influencers WHERE influencer_id = %s",
                (int(influencer_id),)
            )
            inf_row = cursor.fetchone()
            if not inf_row:
                continue
                
            inf_cat = inf_row["category"]
            
            # Relaxed Category Filter:
            # Only filter OUT if the influencer HAS a category AND it clearly doesn't match.
            # If influencer category is unknown (None/Empty), allow it (rely on vector sim).
            if campaign_category and inf_cat:
                cat1 = campaign_category.lower()
                cat2 = inf_cat.lower()
                
                # Check for overlap (e.g. "Tech" in "Science & Technology")
                if cat1 not in cat2 and cat2 not in cat1:
                    continue

            score = inf["similarity"]
            
            cursor.execute("""
                INSERT INTO ranking_scores (
                    campaign_id, influencer_id, raw_score, normalized_score, 
                    rank_position, confidence_level
                )
                VALUES (%s,%s,%s,%s,%s,%s)
                ON DUPLICATE KEY UPDATE
                    normalized_score=VALUES(normalized_score)
            """, (
                campaign_id, 
                int(influencer_id), 
                float(score), 
                float(score), 
                i + 1, 
                0.5  # Lower confidence for cold start
            ))
            
            results.append({
                "rank": i + 1,
                "influencer_id": int(influencer_id),
                "score": float(score)
            })
            
        conn.commit()
        return results

    model = joblib.load(MODEL_PATH)

    X = df[FEATURES].fillna(0)
    scores = model.predict(X)

    df["score"] = scores

    df = df.sort_values("score", ascending=False)

    results = []

    for i, row in df.iterrows():
        influencer_id = row["influencer_id"]

        # 🔐 SAFETY CHECK
        cursor.execute(
            "SELECT 1 FROM influencers WHERE influencer_id = %s",
            (int(influencer_id),)
        )
        if cursor.fetchone() is None:
            continue

        cursor.execute("""
            INSERT INTO ranking_scores (
                campaign_id,
                influencer_id,
                raw_score,
                normalized_score,
                rank_position,
                confidence_level
            )
            VALUES (%s,%s,%s,%s,%s,%s)
            ON DUPLICATE KEY UPDATE
              raw_score=VALUES(raw_score),
              normalized_score=VALUES(normalized_score),
              rank_position=VALUES(rank_position),
              confidence_level=VALUES(confidence_level)
        """, (
            campaign_id,
            int(influencer_id),
            float(row["score"]),
            float(row["score"]),
            i + 1,
            min(1.0, float(row["score"]))
        ))

        results.append({
            "rank": i + 1,
            "influencer_id": int(influencer_id),
            "score": float(row["score"])
        })

    conn.commit()
    return results
