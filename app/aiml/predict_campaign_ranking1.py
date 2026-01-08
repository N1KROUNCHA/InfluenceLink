import os
import pandas as pd
import joblib
import numpy as np
from app.db.mysql import conn, cursor
from app.db.mongo import db
from app.aiml.faiss_search import search_similar

MODEL_PATH = "models/campaign_rank_model.pkl"
METRICS_PATH = "models/model_metrics.joblib"

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
    print(f"🔮 [ML] Running ranking for Campaign {campaign_id}...")
    
    # 1. Load Model
    if not os.path.exists(MODEL_PATH):
        print("⚠️ Model pkl not found. Training now...")
        from app.aiml.train_campaign_match_model1 import train_campaign_model
        train_campaign_model()
    
    model = joblib.load(MODEL_PATH)
    
    # 2. Get Campaign Data & DNA
    cursor.execute("SELECT * FROM campaigns WHERE campaign_id = %s", (campaign_id,))
    campaign = cursor.fetchone()
    if not campaign:
        return []
        
    campaign_dna = db.campaign_dna.find_one({"campaign_id": campaign_id})
    if not campaign_dna or "embedding" not in campaign_dna:
        # Rebuild DNA if missing
        from app.agents.brand_dna.brand_dna_builder import build_brand_dna
        campaign_dna = build_brand_dna(campaign)
        
    # 3. Find Candidate Influencers (Wide net via Vector Sim)
    candidates = search_similar(campaign_dna["embedding"], top_k=500)
    if not candidates:
        return []

    # 4. Feature Engineering for ML
    candidate_ids = [c["influencer_id"] for c in candidates]
    sim_lookup = {c["influencer_id"]: c["similarity"] for c in candidates}
    
    # Fetch influencer data from MySQL
    placeholders = ','.join(['%s'] * len(candidate_ids))
    cursor.execute(f"SELECT * FROM influencers WHERE influencer_id IN ({placeholders})", tuple(candidate_ids))
    influencer_rows = cursor.fetchall()

    ml_data = []
    for row in influencer_rows:
        inf_id = row["influencer_id"]
        dna_sim = sim_lookup.get(inf_id, 0.5)
        
        # Calculate topic overlap
        campaign_topics = set(campaign_dna.get("topics", []))
        inf_dna = db.influencer_dna.find_one({"influencer_id": inf_id})
        inf_topics = set(inf_dna.get("topics", [])) if inf_dna else set()
        overlap = len(campaign_topics.intersection(inf_topics)) / max(1, len(campaign_topics))

        # Build feature vector
        features = {
            "influencer_id": inf_id,
            "subscriber_count": row["subscriber_count"] or 0,
            "avg_views": row["avg_views"] or 0,
            "engagement_score": row["engagement_score"] or 0,
            "authenticity_score": row["authenticity_score"] or 0.8,
            "dna_similarity": float(dna_sim),
            "topic_overlap": float(overlap),
            "category_match": 1.0 if row["category"] == campaign["category"] else 0.0,
            "style_match": 1.0 if row["style"] == campaign["required_style"] else 0.0,
            "region_match": 1.0 if row["region"] == campaign["target_region"] else 0.0
        }
        ml_data.append(features)

    if not ml_data:
        return []

    # 5. ML Prediction
    df_features = pd.DataFrame(ml_data)
    X = df_features[FEATURES].fillna(0)
    
    # Predict "Quality Scores" using the Regressor
    scores = model.predict(X)
    df_features["ml_score"] = scores
    
    # 6. Rank and Save
    df_features = df_features.sort_values("ml_score", ascending=False)
    
    results = []
    for i, (_, row) in enumerate(df_features.iterrows()):
        rank = i + 1
        inf_id = int(row["influencer_id"])
        # Cap score at 1.0 for database sanity
        ml_score = float(min(1.0, row["ml_score"]))
        
        # Determine Explanation based on top feature (Dynamic & Unique)
        features_scores = {
            "Perfect Niche DNA Match": row["dna_similarity"],
            "Exceptional Audience Engagement": row["engagement_score"] * 5, # Scored 0-1, amplified for comparison
            "Strong Topic Synergy": row["topic_overlap"],
            "High Campaign Relevance": (row["category_match"] + row["region_match"]) / 2
        }
        # Pick the feature with the highest relative score
        explanation = max(features_scores, key=features_scores.get)

        cursor.execute("""
            INSERT INTO ranking_scores (
                campaign_id, influencer_id, raw_score, normalized_score, 
                rank_position, confidence_level
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                normalized_score = VALUES(normalized_score),
                rank_position = VALUES(rank_position)
        """, (campaign_id, inf_id, ml_score, ml_score, rank, 0.9)) # ML confidence is high

        # Save Explanation
        cursor.execute("""
            INSERT INTO ranking_explanations (campaign_id, influencer_id, explanation)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE explanation = VALUES(explanation)
        """, (campaign_id, inf_id, explanation))

        results.append({
            "rank": rank,
            "influencer_id": inf_id,
            "score": ml_score,
            "explanation": explanation
        })
        
        # Limit to top 100 for storage efficiency
        if i >= 100: break

    conn.commit()
    return results
